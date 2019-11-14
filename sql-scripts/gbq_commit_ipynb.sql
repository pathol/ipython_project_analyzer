#Alle Commits die auf Jupyter Notebooks ausgeführt wurden
#standardSQL
SELECT *
FROM `githubmining-237707.github_samples.commits_ipynb`
left join unnest(difference) as diff
WHERE ENDS_WITH(diff.new_path,'.ipynb')