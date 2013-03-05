#!/usr/bin/env python
"""
HTML Builder
This was created to provide an object-orient interface for creating HTML.
The core desire was to make tables easier to build.
"""
__author__ = "Jesse Kretschmer"

import cgi
import sys

class Element(object):
	validAttributes = [ 'title',
						'alt',
						'style',
						'id',
						'name',
						'type',
						'class',
					  ]

	def __init__(self, tagName, content=None, parent=None, selfClosing=False, id=None):
		self.tag = tagName
		self.classes = []
		self.parent = parent
		self.children = []
		self.selfClosing = selfClosing
		if id is not None:
			self.id = id
		if content!=None:
			self.addChild(content)

	def setClass(self, className):
		self.classes = [str(className)]
	def addClass(self, className):
		className = str(className)
		if className not in self.classes:
			self.classes.append(className)
	def removedClass(self, className):
		className = str(className)
		while className in self.classes:
			self.classes.remove(className)
	def getClassStr(self):
		return " ".join(self.classes)

	def getContent(self,level):
		returnStr = ''
		for child in self.children:
			if type(child) == str:
				returnStr+="%s\n"%child
			else:
				childStr = child.__str__(level+1)
				if childStr==None:
					raise TypeError("child(%s) %s is none", (type(child).__name__, child))
				returnStr+=child.__str__(level+1)
		return returnStr

	def __str__(self,level=0):
		attrs = []
		for x in self.validAttributes:
			valString = str(getattr(self,x))
			if valString!='':
				attrs.append('%s="%s"' % (x, cgi.escape(valString, True)))

		returnString = ''
		#returnString += "    "*level
		returnString += '<%s ' % self.tag
		returnString += ' '.join(attrs)
		if self.selfClosing:
			returnString +="/>"
		else:
			returnString += '>%s\n' % self.getContent(level)
			returnString += '%s</%s>\n' % ("    "*level, self.tag)
		return returnString

	def setParent(self, parent):
		if type(parent)!=Element:
			raise TypeError("parent must be object of Element type.")
		if self.parent != None:
			self.parent.removeChild(self)
		self.parent = parent
		self.parent.addChild(self)

	def removeParent(self):
		if self.parent != None:
			self.parent.removeChild(self)
		self.parent = None

	def addChild(self,child):
		if type(child) not in [Element, HtmlTable, Style, str]:
			raise TypeError("child must be of the Element, Style or str type.")
		self.children.append(child)
		return child

	def removeChild(self,child):
		for x in self.children:
			if x == child:
				x.removeParent()
			self.children.remove(x)
	def empty(self):
		self.children = []

	def __getattr__(self, attr):
		if attr=='class':
			return self.getClassStr()
		elif attr in ['innerHTML', 'content']:
			return self.getContent()
		elif attr in self.validAttributes:
			return ''
		else:
			raise AttributeError("Can't find attribute %s" % attr)
	def __setattr__(self, attr, value):
		if attr in ['innerHTML', 'content']:
			self.empty()
			self.addChild(value)
		else:
			object.__setattr__(self, attr, value)

class HtmlTable(Element):
	"""
	This object allows the table data to stay in a list of lists for easier manipulation.
	"""
	def __init__(self, *args, **kwargs):
		super(HtmlTable, self).__init__("table",*args, **kwargs)
		self.thead = self.addChild(Element('thead'))
		self.tbody = self.addChild(Element('tbody'))
		self.rows = []
		self.elementClasses = []
		self.elementIds = []
		self.rowClasses = []
		self.rowIds = []
	def addRow(self,rowList=[]):
		self.rows.append(rowList)

	def setMatrix(self, matrix):
		# Accepts list of lists
		if type(matrix) == list:
			self.rows = matrix
		else:
			raise TypeError("matrix must be of type list.")
		return matrix
	def addCellClass(self,rowNum,colNum,className):
		self.elementClasses.append((rowNum,colNum,className))

	def addRowClass(self,rowNum,className):
		self.rowClasses.append((rowNum,className))

	def setRowClass(self,rowNum,className):
		for i,en in enumerate(self.rowClasses):
			if en[0]==rowNum:
				self.rowClasses.remove(i)
		self.addRowClass(rowNum,className)
	def setCellClass(self,rowNum,colNum,className):
		for i,en in enumerate(self.elementClasses):
			if en[0]==rowNum and en[1]==colNum:
				self.elementClasses.remove(i)
		self.addCellClass(rowNum,colNum,className)

	def __str__(self,level=0):
		self.tbody.empty()
		numCols = 0

		# Get the maximal column count
		for rowData in self.rows:
			if len(rowData)>numCols:
				numCols = len(rowData)

		for rowNum,rowData in enumerate(self.rows):
			tr = self.tbody.addChild(Element('tr'))
			for i,en in enumerate(self.rowClasses):
				if en[0]==rowNum:
					sys.stderr.write("Adding class to row %s: %s\n" % (rowNum,en[1]))
					tr.addClass(en[1])
			for colNum in range(numCols):
				td = None
				content = ''
				if colNum < len(rowData):
					content = rowData[colNum]

				if type(content) == Element and content.tag == 'td':
					td = content
				else:
					td = Element('td')
					td.content = content

				for i,en in enumerate(self.elementClasses):
					if en[0]==rowNum and en[1]==colNum:
						td.addClass(en[2])
				tr.addChild(td)
		return super(HtmlTable, self).__str__(level)


class Style(object):
	def __init__(self, names, values = {}):
		if type(names) == str:
			names = [names]
		self.names = names
		self.values = values
	def __str__(self, level=0):
		# level is ignored for css styles
		returnStr = ", ".join(self.names)
		returnStr += "{"
		for k,v in self.values.items():
			returnStr+= " %s: %s;" % (k,v)
		returnStr += "}\n"
		return returnStr

class Builder(object):
	def __init__(self, title=''):
		self.styles = []
		self.html = Element("html")
		self.head = self.html.addChild(Element("head"))
		self.title = self.head.addChild(Element("title",title))
		self.style = self.head.addChild(Element("style"))
		self.style.type = "text/css"
		self.body = self.html.addChild(Element("body"))
		
	def __str__(self):
		return str(self.html)


def example():
	"""
	Example Usage:
	"""
	# HTML Creation
	myPage = Builder(title="Test Page: Hello World 123")
	mainDiv = myPage.body.addChild(Element("div","Hello World!", id="main"))
	mainDiv.addChild(Element("hr", selfClosing=True))
	mainDiv.addChild(Element("h1","Test Title"))
	myTable = mainDiv.addChild(HtmlTable())

	myData = [
	['A','b','c','d'],
	['e','F','g','h'],
	['i','j','K','l'],
	['m','n','o','P'],
	['q','r',Element('td',"S"),'t','u'],
	['v','W','x','y','z'],
	]

	myTable.setMatrix(myData)
	myTable.addRowClass(3,'red')
	myTable.addCellClass(0,2,'awesome')

	# Style definitions
	myPage.style.addChild(Style("body",{'font-family':'Helvetica, Arial, Sans-Serif'}))
	myPage.style.addChild(Style("#main",{'border':'solid 1px grey'}))
	myPage.style.addChild(Style(".red",{'background':'red!important'}))
	myPage.style.addChild(Style(".awesome",{'border':'dotted goldenrod 3px'}))
	myPage.style.addChild(Style("table",{'border-collapse':'collapse','width':'100%'}))
	myPage.style.addChild(Style("td",{'padding':'4px','margin':'0px'}))
	myPage.style.addChild(Style("tr:nth-child(even)",{'background':'#ddd'}))

	# Calling the page as a string will render the html.
	print myPage

if __name__=='__main__':
	example()