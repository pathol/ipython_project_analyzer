#Alle Jupyter Notebooks mit der Anzahl verschiedenen Autoren
#standardSQL
SELECT * EXCEPT(new_path, repo)
FROM `githubmining-237707.github_samples.content_ipynb` a
LEFT JOIN 
(SELECT repo, new_path, count(distinct author.email) contributors
FROM `githubmining-237707.github_samples.commits_ipynb_only`
LEFT JOIN unnest(repo_name) repo
GROUP BY repo,new_path) b
ON a.sample_repo_name = repo
WHERE a.sample_path = b.new_path