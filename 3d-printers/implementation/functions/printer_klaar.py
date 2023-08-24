"""
Move a print job to the folder VERWERKT.
"""

import glob
import sys

from mail_functions import send_response_mail
from directory_functions import (
    job_name_to_global_path,
    copy_print_job,
    does_job_exist_in_main_folder,
    job_name_to_job_folder_name)

from talk_to_sa import yes_or_no
from cmd_farewell_handler import (
    open_gesliced_folder_cmd_farewell,
    remove_directory_and_close_cmd_farewell)

if __name__ == '__main__':

    job_name = sys.argv[1]
    job_global_path = job_name_to_global_path(
        job_name, search_in_main_folder='AAN_HET_PRINTEN')

    if does_job_exist_in_main_folder(job_name, "GESLICED"):
        job_name_folder = {job_name_to_job_folder_name(
            job_name, search_in_main_folder="GESLICED")}
        print(f'Warning! found GESLICED/{job_name_folder}, the print job is not yet ready')
        if yes_or_no(f'do you want to open GESLICED/{job_name_folder} (Y/n)?'):
            # TODO: open the gesliced/job, not gesliced
            open_gesliced_folder_cmd_farewell()

        elif not yes_or_no('you are really sure this print job is done (Y/n)?'):
            print('aborting...')
            sys.exit(0)

    # send response mail
    msg_file_paths = list(glob.glob(job_global_path + "/*.msg"))

    if len(msg_file_paths) > 1:
        print(f'Warning! more than one: {len(msg_file_paths)} .msg files detected')
        input('press enter to send response mail...')

    if len(msg_file_paths) > 0:
        # TODO: this is not a proper response mail bro, fix that
        send_response_mail(msg_file_paths[0], "standard_response.html", {'{response_text}': "Your print is finished! You can pick it up in the IWS"})
        input('press enter to continue. . .')
    else:
        print(f'folder: {job_global_path} does not contain any .msg files,'\
                f'no response mail can be send')

    copy_print_job(job_name, "VERWERKT", source_main_folder='AAN_HET_PRINTEN')
    remove_directory_and_close_cmd_farewell()