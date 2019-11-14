#Alle Commits von Repositories in denen ein Jupyter Notebook vorkommt
#standardSQL
SELECT *
FROM `bigquery-public-data.github_repos.commits`
WHERE commit IN 
(SELECT distinct commit FROM `bigquery-public-data.github_repos.commits`
left join unnest(repo_name) as single_repo_name
where single_repo_name IN (SELECT DISTINCT(sample_repo_name) FROM `githubmining-237707.github_samples.content_ipynb`))