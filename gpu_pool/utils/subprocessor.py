import subprocess as sp


def train(command) -> sp.CompletedProcess[str]:
    return sp.run(command, capture_output=True, text=True, shell=True)


def handle_setup(command) -> sp.CompletedProcess[str]:
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

    while True:
        output = process.stdout.readline().decode()

        if output == "" and process.poll() is not None:
            return process
        if output:
            print(output.strip())
