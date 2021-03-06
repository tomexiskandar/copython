-- drop table Test.dbo.routes
-- delete table Test.dbo.routes
/*
 * how many rows
 */
select count(*) record_count
from test.dbo.routes


SELECT TOP (3) [route_id]
      ,[route_short_name]
      ,[route_long_name]
      ,[route_desc]
      ,[route_type]
      ,[route_url]
      ,[route_color]
      ,[route_text_color]
  FROM [Test].[dbo].[routes]