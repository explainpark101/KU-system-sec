import os, sys
import asyncio
from apps.init import init_all
try:
    from apps.gui import runGUI
except ImportError:
    from apps.init import check_dependencies
    from apps.utils.MessageBox import alert
    check_dependencies()
    alert("Please Restart the program.")
    sys.exit(0)



async def tracking():
    ...
async def create_gui():
    ...
    
    

def main(argv):
    init_all()
    runGUI()


if __name__ == "__main__":
    main(sys.argv)