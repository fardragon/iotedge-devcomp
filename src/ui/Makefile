CC=pyuic5

main_window: main_window.ui | generated_dir
	$(CC) main_window.ui -o generated/main_window.py


generated_dir:
	mkdir -p generated