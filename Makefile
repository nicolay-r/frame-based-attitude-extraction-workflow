install:
    # Install AREkit dependency
    git clone --single-branch --branch 0.19.5-bdr-elsevier-2020-py3 git@github.com:nicolay-r/AREkit.git core

    # Download python dependencies
    pip install -r requirements.txt
