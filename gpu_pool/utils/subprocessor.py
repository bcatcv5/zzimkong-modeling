import subprocess as sp


def train(command) -> sp.CompletedProcess[str]:
    # return sp.run(command, capture_output=True, text=True, shell=True)
    return sp.run(command, capture_output=False, text=True, shell=True)


def handle_setup(command) -> sp.CompletedProcess[str]:
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=True, universal_newlines=True)

    while True:
        output = process.stdout.readline()

        if output == "" and process.poll() is not None:
            return process
        if output:
            print(output.strip())
