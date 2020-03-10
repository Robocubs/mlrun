# Clean up the development system folder.
find . -path "*/*.pyc" -delete
find . -path "*/*.pyo" -delete
find . -path "*/__pycache__" -type d -exec rm -r {} ';'

# Get the IP address. This might be automated in the future with a static IP.
echo "What is the IP address of the Jetson? "
read ip

# Aliasing.
sshp() {
  # Run a command over SSH and redirect the output to the terminal
  sshpass -p 1701robocubs ssh -oStrictHostKeyChecking=accept-new nvidia@$1 "$2"
}
rsyncp() {
  # Copy a file over SSH
  sshpass -p 1701robocubs rsync --progress -avz -e ssh $2 nvidia@$1:$3
}

# Note, the username and password are not like state secrets, and they aren't very secure on purpose.
echo "Stopping MLRun on remote host..."
sshpass -p 1701robocubs ssh -oStrictHostKeyChecking=accept-new nvidia@$ip 'sudo systemctl stop mlrun.service'

# Now, start copying files.
echo "Copying files..."
for filename in mlrun v1 v1tpu v2 v2tpu v3 v3tpu requirements.txt; do
    sshpass -p 1701robocubs rsync --progress -avz -e ssh $filename nvidia@$ip:/home/nvidia/mlrun
done

echo "Updating SystemD service..."
sshpass -p 1701robocubs rsync --progress -avz -e ssh mlrun.service nvidia@$ip:/lib/systemd/system/mlrun.service

# Start the service again.
echo "Starting MLRun on the remote host..."
sshpass -p 1701robocubs ssh -oStrictHostKeyChecking=accept-new nvidia@$ip 'sudo systemctl daemon-reload && sudo systemctl start mlrun.service'
echo "If no errors appeared, the process successfully completed."
