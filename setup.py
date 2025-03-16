from setuptools import setup, find_packages
from typing import List


HYPEN_E_DOT = "-e ."
def get_requirements(file_path:str)->List[str]:
    """
    This function will return a list of requirements

    Args:
        file_path (str): _description_

    Returns:
        List[str]: _description_
    """
    with open(file_path) as file:
        requirements = file.readlines()
        requirements = [req.replace("\n", " ") for req in requirements]
        
        
        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    
    
    return requirements


setup(
    name='Question Paper Generator',
    version='0.0.1',
    author= "Aditya",
    author_email='aditya@example.com',
    packages=find_packages(),
    install_requires = get_requirements("requirements.txt")
)