from setuptools import setup, find_packages

setup(
    name="runelite_plugin",
    version="0.1",
    packages=find_packages(),
)

# pip install -e .



cd C:\Users\asd\Desktop\project

git add .

git commit -m "Update: 10.1"

git push origin main


xcopy "C:\Users\asd\IdeaProjects\runelite\runelite-client\src\main\java\net\runelite\client\plugins\asd" java /s /e /h /i7
git add java/
git commit -m "Update: 16.1"
git push origin main



git rm --cached java -r

git add -f java/.
cd java/runelite-client/src/main/java/net/runelite/client/plugins/asd/
# git add -f java/runelite-client/src/main/java/net/runelite/client/plugins/asd/.

git commit -m "Update: 16.1"

git push origin main
















cd C:\Users\asd\Desktop\project
git add python/
xcopy "C:\Users\asd\IdeaProjects\runelite\runelite-client\src\main\java\net\runelite\client\plugins\asd" java /s /e /h /i /y
git add java/
git commit -m "Update: 16.2"
git push origin main