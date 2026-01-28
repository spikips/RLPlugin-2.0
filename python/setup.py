from setuptools import setup, find_packages

setup(
    name="runelite_plugin",
    version="0.1",
    packages=find_packages(),
)

# pip install -e .


cd C:\Users\asd\Desktop\project
git add python/
xcopy "C:\Users\asd\IdeaProjects\runelite\runelite-client\src\main\java\net\runelite\client\plugins\asd" java /s /e /h /i /y
git add java/
git commit -m "Update: 28.1"
git push origin main