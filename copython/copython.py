"""
copython is an engine to copy data to and from sql database.
it defines functions to be called by client codes.
the arg is an xml config file. this file will be used to 
create/complete metadata for the source and target.
"""
import xml.etree.ElementTree as ET
import xml.dom.minidom
import codecs
import pyodbc
import os
import sys
import io
from multiprocessing import Pool, freeze_support
import multiprocessing
import threading
import csv
import datetime
import time
import itertools


"""
internal copython
"""
from copython import copyconf
from copython import metadata
from copython import rec_gen
from copython import sql_rec
from copython import rec_load
from copython import misc



"""
implementation
define interfaces for client's codes
"""

def copy_data(config, debug=False, insert_method='batch', multi_process=False):
    #try:
        #optional parameters for config
        optional = {}
        optional['debug'] = debug
        optional["insert_method"] = insert_method
        #print(pyodbc.drivers())
        #quit()

        #cc = copyconf.CopyConf.config_from_xml(config)
        cc = copyconf.CopyConf(config)
        #for c in cc.copy_list:
        #    for k,v in c.__dict__.items():
        #        print(k,v)
        
        if debug:
            cc.debug()
        #cc.validate() must make two validation. one validation about the correct config (complete) and validation about source path/table exists
        
        ##### validate config #####
        # does the source file/sql table exist and complete? if not quit

        # does the source can be accessed or connected? if not quit
   
        
    
    
        if multi_process is True:
            copies = []
            copies =  [c for c in cc.copy_list]
            for copy in copies:
                copy.optional = optional
                with Pool(processes=4) as pool:
                    p = pool.map(execute_copy,copies)
        else:
            for copy in cc.copy_list:
                copy.optional = optional
                execute_copy(copy)
    #    return 0
    #except Exception as e: 
    #    return e
def execute_copy(copy):
    start = datetime.datetime.now()
    spinner = itertools.cycle(['-', '\\', '|', '/'])
    ############################### 
    # source type info and metadata
    ###############################
    #create type info and metadata for the source
    if copy.source.__class__.__name__ == "CSVConf":
        if copy.source.delimiter == '\\t':
           copy.source.delimiter = '\t'
        src_md = metadata.CSVMetadata(copy.source)
    elif copy.source.__class__.__name__ == "SQLTableConf":
        #unnecessary at the moment--> src_ti = metadata.SQLTypeInfo(copy.source)
        src_md = metadata.SQLTableMetadata(copy.source)
    elif copy.source.__class__.__name__ == "SQLQueryConf":
        src_md = metadata.SQLQueryMetadata(copy.source)
    
    #if copy.optional['debug']:
    #    print("source metadata: {}".format(src_md.__class__.__name__))
    

    ############################### 
    # target type info and metadata
    ###############################
    if copy.target.__class__.__name__ == "CSVConf":
        print("copy.target as CSV is not allowed at the moment")
        quit()
    elif copy.target.__class__.__name__ == "SQLTableConf":
        trg_ti = metadata.SQLTypeInfo(copy.target)
        #### check if target table exists, if not just create one assumming user wants a dump copy eg. without column mappings
        _is_trg_tbl_existence = metadata.is_sql_table_existence(copy.target)
        if _is_trg_tbl_existence:
            copy.target.table_existence = True
        else:
            copy.target.table_existence = False
            if copy.optional['debug']:
                print("table {}.{} does not exist!".format(copy.target.schema_name,copy.target.table_name))
            thrd = threading.Thread(target=metadata.create_simple_sql_table,args=(copy.target,trg_ti,src_md,copy.optional))
            thrd.start()
            while thrd.is_alive():
                if copy.optional['debug']:
                    #print("|", end='', flush=True)
                    sys.stdout.write(next(spinner))   # write the next character             
                    sys.stdout.flush()                # flush stdout buffer (actual character display)
                    sys.stdout.write('\b')            # erase the last written char
                time.sleep(1)
                
            #synchronous call --> metadata.create_simple_sql_table(copy.target,trg_ti,src_md,copy.optional)
            thrd.join()
            
        trg_md = metadata.SQLTableMetadata(copy.target)
    #if copy.optional['debug']:
    #    print("target metadata: {}".format(trg_md.__class__.__name__))
    
    
    ############################### 
    # SQLRecord instance
    ###############################
    sr = sql_rec.SQLRecord(trg_ti,src_md,trg_md,copy)

    ####validate column matching
    if len(sr.unmatched_column_name_list) > 0:
        print("cannot find matching column(s)  in target table {}.{}: {}".format(",".join(sr.unmatched_column_name_list),trg_md.schema_name,trg_md.table_name))
        quit()
    if len(sr.mapped_column_name_list) == 0:
        print("souce column name: {}".format([x.column_name for x in src_md.column_list]))
        print("target column name: {}".format([x.column_name for x in src_md.column_list]))
        print("Error. column name not fully matching!")
        quit()

    #sr.record_timestamp = record_timestamp
    ##test
    #sr.sql_stmt_type = "prepared"
    max_row_per_batch = None  #define max row per batch
    #### system restriction batch max row = 1000, prepared max param = 2100 
    if max_row_per_batch is None:
        max_row_per_batch = int(0.3*2000/len(sr.mapped_column_name_list))
        if max_row_per_batch < 1:
            max_row_per_batch = 1
    #print("max_row_per_batch {}".format(max_row_per_batch))
    rl = rec_load.RecordLoader(copy.target,trg_md,sr,copy.optional["insert_method"],max_row_per_batch)

    #################################################################### 
    # data source iteration, sql record generation and target processing
    ####################################################################
    row_count = 0


    if copy.optional['debug']:
        print("copying data ",end="",flush=True)
    start_time = time.time()
    for row_count,line in enumerate(rec_gen.record_generator(src_md),1):
        rl.add_record(sr.gen_sql_record(line))      
        #rl.add_record(_record)
        if copy.optional['debug']:
            if row_count % 10000 == 0:
            #if time.time() - start_time > 2:
                #misc.progress()
                sys.stdout.write(str(row_count))
                sys.stdout.flush()
                sys.stdout.write('\b'*len(str(row_count)))
                #start_time = time.time()
    rl.add_record(False)#signal the record loader to finish up
    if copy.optional['debug']:
        sys.stdout.write(str(row_count))
        sys.stdout.flush()
        sys.stdout.write('\b'*len(str(row_count)))
    
    
    if copy.optional['debug']:
        print("copy id {} completed. {} row(s) affected for {}".format(copy.id,row_count,datetime.datetime.now()-start))

def gen_xml_cf_template(target_path,source_type,target_type,conn_str,table_dict):
    """
    create a template config file as xml file.
    if the target_type is a sql_table and colmap is requested then it
    requires to connect to the dbms
    """
    #write the xml file

    root = ET.Element('config')
    child_desc = ET.SubElement(root,"description")
    child_desc.text = "description"
    child_src_type = ET.SubElement(root,"source_type")
    child_src_type.text = source_type
    child_trg_type = ET.SubElement(root,"target_type")
    child_trg_type.text = target_type
    #### add copy
    child_copy = ET.SubElement(root,"copy")
    child_copy.set ("id",table_dict["table_name"])
    ## add copy's child
    #add source
    copy_child_source = ET.SubElement(child_copy,"source")
    copy_child_source.set("path","PUT THE SOURCE PATH HERE")
    copy_child_source_encoding = ET.SubElement(copy_child_source,"encoding")
    copy_child_source_encoding.text = "utf-8-sig"
    copy_child_source_has_header = ET.SubElement(copy_child_source,"has_header")
    copy_child_source_has_header.text = "yes"
    copy_child_source_delimiter = ET.SubElement(copy_child_source,"delimiter")
    copy_child_source_delimiter.text = ","
    copy_child_source_quotechar = ET.SubElement(copy_child_source,"quotechar")
    copy_child_source_quotechar.text = chr(34)
    #add target
    copy_child_target = ET.SubElement(child_copy,"target")
    copy_child_target.set("table_name",table_dict["table_name"])
    copy_child_target.set("schema_name",table_dict["schema_name"])
    copy_child_target_cs = ET.SubElement(copy_child_target,"connection_string")
    copy_child_target_cs_add = ET.SubElement(copy_child_target_cs,"add")
    copy_child_target_cs_add.set("conn_str",conn_str)
    #add column mapping
    if(target_type=="sql_table"):#read the table's columns
        conn = pyodbc.connect(str(conn_str))
        conn.timeout = 15
        cursor = conn.cursor()
        _col_tuple = cursor.columns(table=table_dict["table_name"],schema=table_dict["schema_name"]).fetchall()
        column_name_list = [x.column_name for x in _col_tuple]
        for col in column_name_list:
            child_cm = ET.SubElement(child_copy,"column_mapping")
            child_cm.set("source",col)
            child_cm.set("target",col)
    #add comment for source column name
        #comment = ET.Comment("=========")
        #print(len(column_name_list))
        #child_copy.insert(2+len(column_name_list)+ 1,comment)
    #create an xml string
    xml_str = ET.tostring(root)

    xml_str_parsed = xml.dom.minidom.parseString(xml_str)
   
    pretty_xml_as_string = xml_str_parsed.toprettyxml("  ")
    print(pretty_xml_as_string)

    with codecs.open(target_path, "w", encoding="utf-8") as xml_file:
        xml_file.write(pretty_xml_as_string)

def drop_table(conn_str,schema_name,table_name):
    # check if table exists
    conn = pyodbc.connect(str(conn_str))
    cursor = conn.cursor()
    if cursor.tables(schema=schema_name,table=table_name,tableType="TABLE").fetchone():
        conn = pyodbc.connect(str(conn_str)) 
        cursor = conn.cursor()
        _sql = "DROP TABLE {}.{}".format(schema_name,table_name)
        cursor.execute(_sql)
        conn.commit()
    else:
        # give a warning
        print("Table {}.{} does not exist. function {} was ignored".format(schema_name,table_name,sys._getframe().f_code.co_name))
   



