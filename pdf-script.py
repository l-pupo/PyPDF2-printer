from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import glob
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# JSON LOADER
with open('pdf-data.json','rb') as j:
	data = json.loads(j.read())
#Inputs PATHS
dic_PdfsPath= data["paths"]
inputPath = dic_PdfsPath[0]['input']
inputcropped = dic_PdfsPath[0]['croppedPdfs']
inputmerged = dic_PdfsPath[0]['mergedPdfs']
inputprinted = dic_PdfsPath[0]['printedPdfs']
inputHF = dic_PdfsPath[0]['HFPdfs']
#Slide DATA
cropCoordinates = data["cropCoordinates"]#['UpperLeftXY']['UpperRightXY']['LowerRightXY']['LowerLeftXY']
slide1 = cropCoordinates[0]['Slide1']
slide2 = cropCoordinates[0]['Slide2']
#Text DATA
HFTexts = data["texts"]
textHeader = HFTexts[0]['Header']
textFooter = HFTexts[0]['Footer']


# FUNZIONE CHE ORDINA I PDF
def myPos(e):
    pdf = e.index('.pdf')
    endPath = e.index('/')
    endPath += 1
    stringC = e[endPath:pdf]
    c = int(stringC)
    return c

# RESISTUISCE ARRAY DI NOMI DI FILE ORDINATI
# PESCATI DALLA CARTELLA CROPPED-PDF
# SIA PER MERGER CHE PER PRINTER
def nameList(temp_input):
	names = []
	for filename in os.listdir(temp_input):
		with open(os.path.join(temp_input, filename), 'rb') as f:
			if f.name.endswith('.pdf'):
				names.append(f.name)
	names.sort(key=myPos)	
	return names


# FUNZIONE CROPPER
def cropper():
	# COUNTER PER IL NOME DEL FILE
	numeroFile = 1;

	# CREO LA CARTELLA IN CUI SALVARLI
	dir = os.path.join(inputcropped)
	if not os.path.exists(dir):
		os.mkdir(dir)

	for filename in os.listdir(inputPath):
		with open(os.path.join(inputPath, filename), 'rb') as f:
			if f.name.endswith('.pdf'):
				# DUE ELEMENTI UGUALI PER NON AVERE PROBLEMI CON CROPBOX
				reader1 = PdfFileReader(f.name,'rb')
				reader2 = PdfFileReader(f.name,'rb')
				for page in range(reader1.getNumPages()):
					writer1 = PdfFileWriter()
					writer2 = PdfFileWriter()
					page1 = reader1.getPage(page)
					page2 = reader2.getPage(page)

					page1.cropBox.setUpperLeft((slide1['UpperLeftXY'][0], slide1['UpperLeftXY'][1]))
					page1.cropBox.setUpperRight((slide1['UpperRightXY'][0], slide1['UpperRightXY'][1]))
					page1.cropBox.setLowerRight((slide1['LowerRightXY'][0], slide1['LowerRightXY'][1]))
					page1.cropBox.setLowerLeft((slide1['LowerLeftXY'][0], slide1['LowerLeftXY'][1]))

					writer1.addPage(page1)
					outstream = inputcropped +'/'+ str(numeroFile) +'.pdf'
					numeroFile += 1
					with open(outstream,'wb') as out:
						writer1.write(out)

					page2.cropBox.setUpperLeft((slide2['UpperLeftXY'][0], slide2['UpperLeftXY'][1]))
					page2.cropBox.setUpperRight((slide2['UpperRightXY'][0], slide2['UpperRightXY'][1]))
					page2.cropBox.setLowerRight((slide2['LowerRightXY'][0], slide2['LowerRightXY'][1]))
					page2.cropBox.setLowerLeft((slide2['LowerLeftXY'][0], slide2['LowerLeftXY'][1]))

					writer2.addPage(page2)
					outstream = inputcropped +'/'+ str(numeroFile) +'.pdf'
					numeroFile += 1
					with open(outstream,'wb') as out:
						writer2.write(out)

def merger():

	# CREO LA CARTELLA DI DESTINAZIONE
	dir = os.path.join(inputmerged)
	if not os.path.exists(dir):
		os.mkdir(dir)

	writer = PdfFileWriter()

	# ARRAY DI NOMI PDF
	pdfNames = nameList(inputcropped)

	for i in range(len(pdfNames)):
		reader = PdfFileReader(pdfNames[i],'rb')
		for page in range(reader.getNumPages()):
			writer.addPage(reader.getPage(page).rotateClockwise(90))

	mergedsrt= inputmerged + "/"+inputmerged+".pdf"
	with open(mergedsrt, 'wb') as out:
		writer.write(out)


# FUNZIONE CHE STAMPA I PDF IN CROPPED-PDFS 
# A PAGINE DI TRE
def printer():

	# CREO LA CARTELLA IN CUI SALVARLI
	dir = os.path.join(inputprinted)
	if not os.path.exists(dir):
		os.mkdir(dir)

	# ARRAY DI NOMI PDF
	pdfNames = nameList(inputcropped)

	# CREAZIONE DI UN PDF VUOTO A4
	c = canvas.Canvas('emptyfile.pdf', pagesize=A4)
	width, height = A4
	c.showPage()
	c.save()

	writer = PdfFileWriter()
	y = 0.0

	# CONTROLLO SULLA POSIZIONE DEL FILE DA INSERIRE
	counter = 0

	# SCRIVO IL NUMERO DI PDF PROCESSATI
	print('Numero di pdf processati:',len(pdfNames))

	for i in range(len(pdfNames)):
		# CONTROLLO SE C'È DA CONSIDERARE UNA NUOVA PAGINA
		if counter == 0:
			emptyPage = PdfFileReader('emptyfile.pdf')
			x1 = (emptyPage.getPage(0).mediaBox.getWidth()/2)
			fx1 = float(x1)
			counter += 1
    
		# ASSEGNO AL READER DI TURNO IL PDF DI TURNO
		reader = PdfFileReader(pdfNames[i],'rb')

		#TROVO LA X CENTRATA E LA Y
		x2 = (reader.getPage(0).cropBox.getWidth()/2)
		fx2 = float(x2)
		centered_X = fx1-fx2

		# A CAUSA DELLA GESTIONE DEI RITAGLI PDF,
		# È NECESSARIO TRATTARLI DIVERSAMENTE 
		# A SECONDA CHE SIANO LA METÀ DI SOPRA O DI SOTTO 
		stringPos = pdfNames[i].index('.pdf')
		stringPos -= 1
		pos = int(pdfNames[i][stringPos])

		# CASO PRIMO PDF DELLA PAGINA
		if counter == 1:

			if (pos%2 != 0):
				y = 200
			else:
				y = 460

		if counter == 2:

			if (pos%2 != 0):
				y = -30
			else:
				y = 230

		if counter == 3:

			if (pos%2 != 0):
				y = -260
			else:
				y = 0
    
		emptyPage.getPage(0).mergeScaledTranslatedPage(reader.getPage(0),0.75,centered_X,y)

		if i == (len(pdfNames)-1):
			writer.addPage(emptyPage.getPage(0))
		elif (counter == 3):
			writer.addPage(emptyPage.getPage(0))
			counter = -1

		# AGGIORNO IL COUNTER
		counter += 1


	with open(inputprinted+ '/' + inputprinted +'.pdf', "wb") as outputStream:
		writer.write(outputStream)

	os.remove('emptyfile.pdf')

def HFPrinter():
	# Manca il ciclo per tutte le pagine 
	# Tenere conto del numero pagina per compilare il footer automatico.

	# Creo la cartella in cui salvarli
	dir = os.path.join(inputHF)
	if not os.path.exists(dir):
		os.mkdir(dir)

	PAGE_WIDTH  = A4[0]
	PAGE_HEIGHT = A4[1]
	center = (PAGE_WIDTH/2)
	pageCount = 1
	
	for filename in os.listdir(inputprinted):
		with open(os.path.join(inputprinted,filename),'rb') as f:
			if f.name.endswith('.pdf'):
				printed = PdfFileReader(f.name,'wb')
				for page in range(printed.getNumPages()):
					can = canvas.Canvas("canvas.pdf", pagesize=A4)
					# Registrare qui altri font
					pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
					can.setFont('Arial', int(textHeader['fontSize']))

					# Print di Header e footer	
					can.drawCentredString(center, PAGE_HEIGHT - 20 - int(textHeader['Margin']), textHeader['text'])

					if(textFooter['text'] == ""):
						footerText = str(page+1) + "/" + str(printed.getNumPages())
					else:
						footerText = textFooter['text']
					
					can.drawCentredString(center, 10 + int(textFooter['Margin']), footerText)
					can.save()
					# APRO L'HEADER / FOOTER APPENA CREATO
					new_pdf = PdfFileReader("canvas.pdf")
					output = PdfFileWriter()
					merging_page = printed.getPage(page)
					merging_page.mergePage(new_pdf.getPage(0))
					output.addPage(printed.getPage(page))
					
					with open(inputHF+"/"+str(pageCount)+".pdf", 'wb') as out:
						output.write(out)
					pageCount += 1

	os.remove('canvas.pdf')
	writer = PdfFileWriter()
	# ARRAY DI NOMI PDF
	pdfNames = nameList(inputHF)

	for i in range(len(pdfNames)):
		reader = PdfFileReader(pdfNames[i],'rb')
		for page in range(reader.getNumPages()):
			writer.addPage(reader.getPage(page))

	with open(inputHF+"/"+inputHF+".pdf", 'wb') as out:
		writer.write(out)

	for i in range(len(pdfNames)):
		os.remove(pdfNames[i])





def printMenu():
	print('--------------------')
	print('Che azione vuoi fare?')
	print('1) Cropper')
	print('2) Merger')
	print('3) Printer')
	print('4) Header e footer printer')
	print('5) Exit')
	choose = input()
	return choose

# MAIN
navigator = (printMenu())
while(navigator != '5'):

	if(navigator == '1'):
		print("Vuoi specificare un nome per la path di input? (default:"+ inputPath +")")
		userChoice = input()
		if(userChoice != ''):
			inputPath = userChoice
		print("Vuoi specificare un nome per la path salvataggio? (default:"+ inputcropped + ")")
		userChoice = input()
		if(userChoice != ''):
			inputcropped = userChoice
		cropper()

	elif(navigator == '2'):
		print("Vuoi specificare un nome per la path di input? (default:"+ inputcropped + ")")
		userChoice = input()
		if(userChoice != ''):
			inputcropped = userChoice	
		merger()

	elif(navigator == '3'):
		print("Vuoi specificare un nome per la path output? (default:"+ inputprinted + ")")
		userChoice = input()
		if(userChoice != ''):
			inputprinted = userChoice	
		printer()

	elif(navigator == '4'):
		print("Vuoi specificare un nome per la path di input? (default:"+ inputprinted + ")")
		userChoice = input()
		if(userChoice != ''):
			inputprinted = userChoice	
		print("Vuoi specificare testo per l'header? (default:"+ textHeader['text'] + ")")
		userChoice = input()
		if(userChoice != ''):
			textHeader['text'] = userChoice
		print(textHeader['text'])
		print("Vuoi specificare testo per il footer? (default:"+ textFooter['text'] + ")")
		userChoice = input()
		if(userChoice != ''):
			textFooter['text'] = userChoice
		print(textFooter['text'])		
		HFPrinter()

	navigator = (printMenu())
