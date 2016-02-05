Copy (
SELECT dp.id as datapoint_id,
	   ds.title as filename, 
	   dp.timestamp as timestamp, dp.value as value,
	   ul.user_id as labeller, users.email as email, ul.label as cooking_label
FROM datasets as ds
INNER JOIN datapoints as dp ON ds.id=dp.dataset_id
INNER JOIN user_labels as ul ON dp.id=ul.datapoint_id
INNER JOIN labelled_datasets as lab_ds ON ds.id=lab_ds.dataset_id AND ul.user_id=lab_ds.user_id
INNER JOIN users ON ul.user_id=users.id
WHERE ds.study_id=[study_id]
ORDER BY ds.id, user, timestamp
) To '/tmp/study_dumps/[study_id]_userlabels.csv' With CSV HEADER;

Copy (
SELECT dp.id as datapoint_id,
	   ds.title as filename, 
	   dp.timestamp as timestamp, dp.value as value
FROM datasets as ds
INNER JOIN datapoints as dp ON ds.id=dp.dataset_id
WHERE ds.study_id=[study_id]
ORDER BY ds.id, timestamp
) To '/tmp/study_dumps/[study_id]_studydata.csv' With CSV HEADER;