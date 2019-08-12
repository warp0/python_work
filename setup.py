import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
        name='tagcounter',
        version='0.1',
        scripts=['main.py'],
        url="https://github.com/warp0/python_work",
        license="MIT",
        author="Roman_Fedoryshyn",
        author_email="roman_fedoryshyn@epam.com",
        description="This is a project, made as a hometask for Python courses at EPAM System. It takes a link and counts html-tags found on the given web-page. Has UI and CL interfaces",
        long_description_content_type="text/markdown",    
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
