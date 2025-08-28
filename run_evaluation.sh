# DO NOT CHANGE THIS
db_root_path='./dev_databases/'
num_cpus=16
meta_time_out=30.0
predicted_sql_path='./output.json' # Replace with your predict sql json path
sql_dialect="SQLite" # ONLY Modify this
base_name=$(basename "$predicted_sql_path" .json)
output_log_path="./eval_result/${base_name}.txt"
diff_json_path="./mini_dev_sqlite_subset.json"
ground_truth_path="./mini_dev_sqlite_gold_subset.sql"

# Output the set paths
echo "Differential JSON Path: $diff_json_path"
echo "Ground Truth Path: $ground_truth_path"




echo "starting to compare with knowledge for ex, sql_dialect: ${sql_dialect}"
python -u ./evaluation_ex.py --db_root_path ${db_root_path} --predicted_sql_path ${predicted_sql_path}  \
--ground_truth_path ${ground_truth_path} --num_cpus ${num_cpus} --output_log_path ${output_log_path} \
--diff_json_path ${diff_json_path} --meta_time_out ${meta_time_out}  --sql_dialect ${sql_dialect}



# echo "starting to compare with knowledge for R-VES, sql_dialect: ${sql_dialect}"
# python3 -u ./evaluation_ves.py --db_root_path ${db_root_path} --predicted_sql_path ${predicted_sql_path}  \
# --ground_truth_path ${ground_truth_path} --num_cpus ${num_cpus}  --output_log_path ${output_log_path} \
# --diff_json_path ${diff_json_path} --meta_time_out ${meta_time_out}  --sql_dialect ${sql_dialect}


# echo "starting to compare with knowledge for soft-f1, sql_dialect: ${sql_dialect}"
# python3 -u ./evaluation_f1.py --db_root_path ${db_root_path} --predicted_sql_path ${predicted_sql_path}  \
# --ground_truth_path ${ground_truth_path} --num_cpus ${num_cpus}  --output_log_path ${output_log_path} \
# --diff_json_path ${diff_json_path} --meta_time_out ${meta_time_out}   --sql_dialect ${sql_dialect}
