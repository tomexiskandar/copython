/*
 use xxx
 DROP TABLE [dbo].[artg_entry]
 DROP TABLE [dbo].[sponsor]
 DROP TABLE [dbo].[manufacturers]
 DROP TABLE [dbo].[products]
*/
/*
USE Test
delete from [dbo].[artg_entry]
delete from [dbo].[sponsor]
delete from [dbo].[manufacturers]
delete from [dbo].[products]
delete from [dbo].[contacts]
*/
use Test
SELECT s.name,o.name,
  ddps.row_count 
FROM sys.indexes AS i
  INNER JOIN sys.objects AS o ON i.OBJECT_ID = o.OBJECT_ID
  INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
  INNER JOIN sys.dm_db_partition_stats AS ddps ON i.OBJECT_ID = ddps.OBJECT_ID
  AND i.index_id = ddps.index_id 
WHERE i.index_id < 2  AND o.is_ms_shipped = 0 
ORDER BY s.NAME,o.NAME


SELECT TOP (2) *
  ,CONVERT(nvarchar(16),SWITCHOFFSET (created_on,'+11:00'),120) as local
  ,SWITCHOFFSET (created_on,'+11:00') as created_on_localtime
  FROM [Test].[dbo].[artg_entry]

SELECT TOP (2) *
FROM [Test].[dbo].[manufacturers]

SELECT TOP (2) *
FROM [Test].[dbo].[products]

SELECT TOP (2) *
FROM [Test].[dbo].[sponsor]

SELECT TOP (2) *
FROM [Test].[dbo].[contacts]


