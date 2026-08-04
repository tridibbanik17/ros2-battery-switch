from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'battery_switch'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tridib Banik',
    maintainer_email='tridib.perfect@gmail.com',
    description='Two battery nodes with a UI node that can switch between them.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'battery_node = battery_switch.battery_node:main',
            'ui_node = battery_switch.ui_node:main',
        ],
    },
)
