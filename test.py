import as608_combo_lib as as608

session = as608.connect_serial_session("COM8")
if session:
	as608.get_templates_list(session)
	as608.get_templates_count(session)
	as608.get_device_size(session)
	# as608.enroll_finger_to_device(session, as608)
	# print(as608.search_fingerprint_on_device(session, as608))
	# as608.enroll_save_to_file(session, as608, "database", "templ1")
	# as608.enroll_save_to_file(session, as608, "database", "templ000000001")
	# as608.fingerprint_check_one_file(session, as608, "database", "templ1")
	# as608.fingerprint_check_one_file(session, as608, "database", "templ000000001")
	as608.fingerprint_check_all_file(session, as608, "database")
else:
	print("EXIT")