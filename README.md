#copython

An ETL program to copy data from and to database.
This program is intended for data analyst, data scientist, data engineer and data warehouse specialist. By this time of writing this file, here the facts:

copython.py is the module that users/clients can use.
Some testings* done and worked as expected.
 
My laptop relevant contents:<br />
Windows 7 64 bit<br />
MS Visual Studio 2017 Community Edition, Python tool for VS<br />
Python 3.6 64 bit<br /> 
*Testings are done with the following servers editions with installed ODBC drivers:

SQL Server version 12.0.200 year 2014 64 bit. ODBC driver 11 for SQL Server<br />
PostgreSQL version 10.1 year 2017 64 bit. ODBC driver PostgreSQL Unicode(x64)<br />
Oracle version 11g Express Edition year 2017 64 bit. ODBC driver Oracle in instantclient_12_2, Oracle in XE<br />
MySQL version 5.7.20 year 2017 64 bit. ODBC driver MySQL ODBC 5.3 Unicode Driver<br />


Successfull copy operations as the following:

copy csv file into SQL Server<br />
copy csv file into  table and vice versa<br />
copy SQL Server select query to PostgreSQL table and vice versa<br />
copy MySQL table and sql query to SQL Server table<br />
copy Oracle sql query to SQL Server<br />
copy Oracle table to SQL Server