CREATE TABLE fileContent (
	[file_path] VARCHAR(1024),
	[content] BLOB,
	[record_time] DATETIME,
	[is_text] BOOLEAN
);


-- SELECT FILE CONTENT FROM Dir
SELECT fileContent.*
FROM fileContent
WHERE fileContent.file_path LIKE '%%s'



-- SELECT FILE CONTENT
SELECT fileContent.*
FROM fileContent
WHERE fileContent.file_path = '%s'
	AND fileContent.record_time = '2023-01-01'