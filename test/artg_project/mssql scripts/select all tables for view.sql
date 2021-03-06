/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (1000) 
      a.[ApprovalArea]
      ,a.[EntryType]
      ,a.[LicenceClass]
      ,a.[LicenceId]
      ,a.[Name]
      ,a.[ProductCategory]
      ,a.[DocumentLink]
      ,a.[StartDate]
      ,a.[Status]
	  ,m.[AddressLine1] as MfrAddressLine1
	  ,m.[AddressLine2] as MfrAddressLine2
	  ,m.[Country] as MfrCountry
	  ,m.[Postcode] as MfrPostcode
	  ,m.[State] as MfrState
	  ,m.[Suburb] as MfrSuburb
	  ,m.[Name] as MfrName
	  ,p.[EffectiveDate] as ProdEffectiveDate
	  ,p.[GMDNCode] as ProdGMDNCode
	  ,p.[GMDNTerm] as ProdGMDNTerm
	  ,p.[Name] as ProdName
	  ,p.[Type] as ProdType
	  ,s.[AddressLine1] as SprAddressLine1
	  ,s.[AddressLine2] as SprAddressLine2
	  ,s.[Country] as SprCountry
	  ,s.[Postcode] as SprPostcode
	  ,s.[State] as SprState
	  ,s.[Suburb] as SprSuburb
	  ,s.[Name] as SprName
  FROM [ARTG].[dbo].[artg_entry] a
  INNER JOIN [ARTG].[dbo].[manufacturers] m
  ON a.LicenceId = m.LicenceId
  INNER JOIN [ARTG].[dbo].[products] p
  ON a.LicenceId = p.LicenceId
  INNER JOIN [ARTG].[dbo].[sponsor] s
  ON a.LicenceId = s.LicenceId
  ORDER BY LicenceId

