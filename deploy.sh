# Clean up the development system folder.
find . -path "*/*.pyc" -delete
find . -path "*/*.pyo" -delete
find . -path "*/__pycache__" -type d -exec rm -r {} ';'

# Knock knock. It's the future. They have hosts. With static IPs. Static hosts.

# Note, the username and password are not like state secrets, and they aren't very secure on purpose.
echo "Stopping MLRun on remote host..."
sshpass -p 1701robocubs ssh -oStrictHostKeyChecking=accept-new nvidia@10.17.1.5 'echo 1701robocubs | sudo -S systemctl stop mlrun.service'

# Now, start copying files.
echo "Copying files..."
for filename in mlrun pyproject.toml requirements.txt buildext.py; do
    sshpass -p 1701robocubs rsync --progress -avz -e ssh $filename nvidia@10.17.1.5:/home/nvidia/mlrun
done

echo "Updating SystemD service..."
sshpass -p 1701robocubs rsync --progress -avz -e ssh mlrun.service nvidia@10.17.1.5:/lib/systemd/system/mlrun.service

# Start the service again.
echo "Starting MLRun on the remote host..."
sshpass -p 1701robocubs ssh -oStrictHostKeyChecking=accept-new nvidia@10.17.1.5 'echo 1701robocubs | sudo -S systemctl daemon-reload && echo 1701robocubs | sudo -S systemctl start mlrun.service'
echo "If no errors appeared, the process successfully completed."
