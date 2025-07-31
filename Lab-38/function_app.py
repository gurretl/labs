import azure.functions as func
import subprocess
import logging
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="function_app")
def function_app(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    azcopy_msi_client_id = os.getenv("AZCOPY_MSI_CLIENT_ID", "Not Set")
    azcopy_auto_login_type = os.getenv("AZCOPY_AUTO_LOGIN_TYPE", "Not Set")
    azcopy_msi_object_id = os.getenv("AZCOPY_MSI_OBJECT_ID", "Not Set")
    azcopy_path = os.path.join(os.getcwd(), "azcopy")

    try:
        command = [
            azcopy_path,
            "list",
            "https://thedevopsrunnersource.blob.core.windows.net"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        response_content = f"AzCopy stdout:\n{result.stdout}\n\nAzCopy stderr:\n{result.stderr}"
        if result.returncode == 0:
            logging.info("AzCopy list command executed successfully.")
            # Now perform the sync command
            sync_command = [
                azcopy_path,
                "sync",
                "https://thedevopsrunnersource.blob.core.windows.net/backup",
                "https://thedevopsrunnerdest.blob.core.windows.net/backup"
            ]
            sync_result = subprocess.run(sync_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            sync_content = f"AzCopy sync stdout:\n{sync_result.stdout}\n\nAzCopy sync stderr:\n{sync_result.stderr}"
            if sync_result.returncode == 0:
                logging.info("AzCopy sync command executed successfully.")
                return func.HttpResponse(f"AzCopy list command executed successfully.\n{response_content}\n\nAzCopy sync command executed successfully.\n{sync_content}", status_code=200)
            else:
                logging.error(f"AzCopy sync command failed with return code {sync_result.returncode}")
                return func.HttpResponse(f"AzCopy list command executed successfully.\n{response_content}\n\nAzCopy sync command failed.\n{sync_content}", status_code=500)
        else:
            logging.error(f"AzCopy list command failed with return code {result.returncode}")
            return func.HttpResponse(f"AzCopy list command failed.\n{response_content}", status_code=500)
    except Exception as e:
        logging.error(f"An error occurred while executing AzCopy commands: {str(e)}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)
