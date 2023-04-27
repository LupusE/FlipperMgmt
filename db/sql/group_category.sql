SELECT
	category
	,COUNT(category)
	
	FROM irfile
	GROUP BY category