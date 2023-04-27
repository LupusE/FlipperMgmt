SELECT	irf.category
		,irb.name
		,btn.button AS mapping
		,irf.file AS filename

	FROM irbutton irb
	LEFT JOIN irfile irf ON (irb.md5hash = irf.md5hash)
	LEFT JOIN btntrans btn ON (irb.name = btn.name)