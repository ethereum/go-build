import sys, os, argparse, logging, shutil, subprocess, stat,glob
from os.path import isfile

# TODO handle icns
# TODO create dmg
# TODO Add client qml files and png files
# CHMOD +x the main binary

logging.basicConfig(
	stream=sys.stdout,
	format='%(asctime)s : %(levelname)s\t : %(message)s',
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.DEBUG
)

XML_PLIST = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleGetInfoString</key>
  <string>Ethereal</string>
  <key>CFBundleExecutable</key>
  <string>Ethereal</string>
  <key>CFBundleIdentifier</key>
  <string>com.ethereum.ethereal</string>
  <key>CFBundleName</key>
  <string>Ethereal</string>
  <key>CFBundleIconFile</key>
  <string>Ethereal.icns</string>
  <key>CFBundleShortVersionString</key>
  <string>POC3</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>POC3</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>IFMajorVersion</key>
  <integer>0</integer>
  <key>IFMinorVersion</key>
  <integer>3</integer>
</dict>
</plist>
"""

RUN_SCRIPT ="""
#!/bin/bash
cd "${0%/*}"
./go-ethereum
"""

class AppBundler:
	def copytree(self, src, dst, symlinks=False, ignore=None):
		for item in os.listdir(src):
			s = os.path.join(src, item)
			d = os.path.join(dst, item)
			if os.path.isdir(s):
				shutil.copytree(s, d, symlinks, ignore)
			else:
				shutil.copy2(s, d)
	
	# If macdeployqt handles qmldir then runs on app
	def runMacDeployQT(self):
		exe = '/usr/local/Cellar/qt5/5.2.0/bin/macdeployqt'
		if not os.path.exists(exe): exe = 'macdeployqt'
		p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		handles_qml = False
		for line in p.stdout.readlines():
			if '-qmldir=<path>' in line:
				handles_qml = True
				break
		if handles_qml and self.go_path is not None:
			qml_path = os.path.join(self.go_path, 'src/github.com/ethereum/go-ethereum/ethereal/assets/qml/') #TODO this is terrible
			command = exe + ' ' + os.path.join(self.output_dir + '/Ethereal.app') + ' -qmldir=' +  qml_path #TODO this is terrible
			logging.info('Running macdeployqt')
			p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			for line in p.stdout.readlines():
				logging.info('macdeployqt: ' + line.strip())
		else:
			logging.error('Your version of macdeployqt does not handle qmldir')
	
	# Add ICNS file to
	def insertICNS(self):
		try:
			shutil.copyfile('./Ethereal.icns', os.path.join(self.output_dir, 'Ethereal.app/Contents/Resources/Ethereal.icns')) # TODO this is horrible
			logging.info('Inserted Ethereal.icns')
		except Exception as e:
			logging.error(str(e))
	
	def insertQMLnPNG(self):
		pass # TODO
	
	#def signApp(self):
		# after macdeployqt copy /usr/local/Cellar/qt5/5.2.0/lib/QtCore.framework/Contents/Info.plist to .app/Contents/Resources/QtCore.framework/Resources/Info.plist
		# codesign --verbose --force --sign "Developer ID Application: <<INSERT DETAILS HERE>>" /Users/_/Dropbox/Experiments/EthereumBuild/Ethereal.app/Contents/Frameworks/QtCore.framework
		# do for rest
		# codesign --verbose --deep --force --sign "Developer ID Application: <<INSERT DETAILS HERE>>" Ethereal.app
		# codesign --verify --verbose=4 Ethereal.app

	# Insert all QML files and other resource files Ethereal needs
	def insertResources(self):
		qml_path = os.path.join(self.go_path, 'src/github.com/ethereum/go-ethereum/ethereal/assets/qml/')
		target_folder = "Ethereal.app/Contents/Resources/"
		target_folder_qml = target_folder + "qml/"

		os.makedirs(target_folder_qml)

		files = glob.glob(qml_path)
		for f in files:
			print "Copying %s to %s" % (f, target_folder_qml)
			
			if isfile(f):
				shutil.copy(f, target_folder_qml)
			else:
				self.copytree(f, target_folder_qml)

		files = glob.glob(os.path.join(self.go_path, 'src/github.com/ethereum/go-ethereum/ethereal/assets/*'))
		for f in files:
			print "Copying %s to %s" % (f, target_folder)
			
			if isfile(f):
				shutil.copy(f, target_folder)
			else:
				self.copytree(f, target_folder)

		

		
	# Finds go-etherum binary and copies to app bundle
	def insertGoBinary(self):
		if self.go_path is not None:
			binary = os.path.join(self.go_path, 'bin/ethereal')
			if os.path.exists(binary):
				try:
					shutil.copyfile(binary, os.path.join(self.output_dir, 'Ethereal.app/Contents/MacOS/Ethereal')) # TODO this is horrible
					os.chmod(os.path.join(self.output_dir, 'Ethereal.app/Contents/MacOS/Ethereal'), 0711)
					logging.info('Inserted go-ethereum binary')
				except Exception as e:
					logging.error(str(e))
			else:
				logging.error('Cannot find go-etherum binary')
				if self.handleHumanInput('Run "go get -u github.com/ethereum/go-ethereum" ?'):
					logging.debug('Not Implemented')
					pass
		
		else:
			logging.error('GOPATH not found, cannot continue')
	
	# Write the Info.plist
	def writePList(self):
		try:
			with open(os.path.join(self.output_dir, 'Ethereal.app/Contents/Info.plist'), 'wb') as f: # TODO this is horrible
				f.write(XML_PLIST)
				f.close()
				logging.info('Info.plist written')
		except Exception as e:
			logging.error(str(e))
	
	# Building out directory structure
	def buildStructure(self, root, structure):
		if root is not self.output_dir:
			try:
				os.mkdir(root)
				logging.info('Created ' + root)
			except Exception as e:
				logging.error(str(e))
				if self.handleHumanInput('Remove Directory?'):
					try:
						shutil.rmtree(root)
						self.buildStructure(root, structure)
						return
					except Exception as e:
						logging.error(str(e))
		for item in structure.keys():
			self.buildStructure(
				os.path.join(root, item),
				structure[item]
			)
	
	# Convert human input to boolean
	def handleHumanInput(self, question=''):
		if self.force: return True
		try:
			answer = raw_input(question + " [Y/n]: ").lower()
		except:
			return True
		if answer is '' or answer[0:1] == 'y': return True
		return False
	
	# Setup Variables
	def __init__(self, args):
		self.force = args['force']
		self.output_dir = args['output']
		self.app_name = "".join(x for x in args['name'] if x.isalnum()) # Simple Santize
		self.app_structure = {
			'%s.app' % self.app_name : {
				'Contents' : {
					'MacOS' : {},
					'Resources' : {}
				}
			}
		}
		self.go_path = os.environ.get('GOPATH')
		self.buildStructure(self.output_dir, self.app_structure)
		self.writePList()
		self.insertICNS()
		self.insertGoBinary()

		self.insertResources()

		self.runMacDeployQT()

		logging.info("fin'")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Standalone Ethereal Go Client App Bundler')
	parser.add_argument('-n','--name', help='Name of app bundle', default='Ethereal', required=False)
	parser.add_argument('-o','--output', help='Directory to write app bundle', default=os.getcwd(), required=False)
	parser.add_argument('-f','--force', help='Force Fresh Build', default=False, required=False)
	args = vars(parser.parse_args())
	AppBundler(args)
