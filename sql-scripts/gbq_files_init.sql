#Alle Jupyter Notebooks 
#standardSQL
SELECT a.id id, size, content, binary, copies,
  sample_repo_name, sample_path
FROM (
  SELECT id, ANY_VALUE(repo_name) sample_repo_name, ANY_VALUE(path) sample_path
  FROM `bigquery-public-data.github_repos.files`
  WHERE ENDS_WITH(path,'.ipynb')
  GROUP BY 1
) a
JOIN `bigquery-public-data.github_repos.contents` b
ON a.id=b.id