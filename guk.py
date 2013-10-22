import StringIO, codecs, tempfile, os, shutil, datetime
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# (n)eu
# (v)ersteht sie
# (k)ann sie
# (p)roduziert sie

# doppelte Eintraege in org Guks
# key exists Maus guk1 guk2
# key exists Buch guk1 guk3
# key exists Ferien guk2 guk3
# key exists Pause guk2 guk3
# key exists rechnen guk2 guk3
# key exists schreiben guk2 guk3
# key exists Stuhl guk1 guk3
# key exists Tisch guk1 guk3
# key exists Weihnachten guk2 guk3


class guk :

  def __init__(self):
    self.now = datetime.datetime.now()
    self.today = str(self.now.year)+str(self.now.month).rjust(2,'0')+str(self.now.day).rjust(2,'0')
    self.data = {}
    self.workd = tempfile.mkdtemp()
    self.curd = os.path.realpath(os.curdir)
    self.guks = [1,2,3]
    self.words = {}
    self.profdict = {'dt': {'n': 'neu',
                            'v': 'versteht',
                            'p': 'produziert',
                            ' ': '' },
                     'fr': {'n': 'nouvelle',
                            'v': 'comprends',
                            'p': 'produis',
                            ' ': ''},
                     'en': {'n': 'new',
                            'v': 'understands',
                            'p': 'produces',
                            ' ': ''}
                     }
    self.coldict = { 'n' : [1,0,0],
                     'v' : [1,1,0],
                     'p' : [0,1,0],
                     ' ' : [1,1,1]
                     }
    self.lang = 'dt'
    self.langs = ['fr', 'dt'] #['fr', 'dt']
    self.tempdir = tempfile.mkdtemp(prefix='guk', suffix='tmp') + os.sep
    self.debug = False
    self.inversedata = {}

  def annotate(self, pict, word, trans, prof, guk) :
    if word[:2] in ['zx','zy','zz'] : word = word[3:]
    # vpos = 0
    # hpos = 0
    # if posv == 't' : vpos = 250
    # elif posv == 'b' : vpos = 27
    # if posh == 'l' : hpos = 5
    # elif posh == 'r' : hpos = 381
    postop = 250
    posbot = 40
    poslft = 5
    posrgt = 381
    gukhor = 170
    gukver = 5
    trhor = -15 #40
    trver = 50

    packet = StringIO.StringIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.rotate(90)
    can.drawString(trver, trhor, trans)
    can.save()
    #move to the beginning of the StringIO buffer
    packet.seek(0)
    transpdf = PdfFileReader(packet)

    packet2 = StringIO.StringIO()
    can2 = canvas.Canvas(packet2, pagesize=letter)
    can2.drawRightString(375, 250, self.profdict[self.lang][prof])
    can2.save()
    packet2.seek(0)
    profpdf = PdfFileReader(packet2)
    
    packet3 = StringIO.StringIO()
    can3 = canvas.Canvas(packet3, pagesize=letter)
    can3.setFontSize(8)
    can3.drawString(gukhor, gukver, guk)
    can3.save()
    packet3.seek(0)
    gukpdf = PdfFileReader(packet3)

    packet4 = StringIO.StringIO()
    can4 = canvas.Canvas(packet4, pagesize=letter)
    can4.setFillColorRGB(self.coldict[prof][0],self.coldict[prof][1],self.coldict[prof][2])
    can4.setStrokeColorRGB(self.coldict[prof][0],self.coldict[prof][1],self.coldict[prof][2])
    can4
    can4.circle(395,254,15,1,1)
    can4.save()
    packet4.seek(0)
    circle = PdfFileReader(packet4)

    if self.lang != 'dt' :
      packet5 = StringIO.StringIO()
      can5 = canvas.Canvas(packet5, pagesize=letter)
      can5.setFontSize(12)
      can5.drawString(40, 10, word)
      can5.save()
      packet5.seek(0)
      wordpdf = PdfFileReader(packet5)
    
    # read your existing PDF
    picfile = file(pict, 'rb')
    existing_pdf = PdfFileReader(picfile)
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(transpdf.getPage(0))
    page.mergePage(profpdf.getPage(0))
    page.mergePage(gukpdf.getPage(0))    
    page.mergePage(circle.getPage(0))
    if self.lang != 'dt' : page.mergePage(wordpdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = file('.'.join(pict.split('.')[:-1])+'-new.pdf', "wb")
    output.write(outputStream)
    outputStream.close()
#    picfile.close()

  def readInputFile(self, file, guk) :
    f = open(file, 'r')
    for l in f.readlines():
      if l[-1] == '\n' : l = l[:-1]
      ls = l.split(',')
      ls.append(guk)
      if self.data.has_key(ls[1]) : print "key exists", ls[1], self.data[ls[1]]['guk'], guk
      self.data[ls[1]] = {}
      self.data[ls[1]]['guk'] = guk
      self.data[ls[1]]['prof'] = ls[0]
      self.data[ls[1]]['dt'] = {'word': ls[1], 'desc':ls[4]}
      self.data[ls[1]]['fr'] = {'word': ls[2], 'desc':ls[5]}
      self.data[ls[1]]['en'] = {'word': ls[3], 'desc':ls[6]}
    f.close()

  def prepareWork(self) :
    for g in self.guks :
      gstr = 'guk' + str(g)
      gdir = self.curd + os.sep + gstr + os.sep
      wordfile = gdir + 'guk-'+gstr+'.csv'
      self.readInputFile(wordfile, gstr)

  def producePictures(self):
    for name in self.data.keys() :
      prof = self.data[name]['prof']
      #if not prof : prof = ' '
      if prof : # True / prof
        self.inversedata[self.data[name][self.lang]['word'].lower()] = name
        guk = self.data[name]['guk']
        trans = self.data[name][self.lang]['desc']
        word = self.data[name][self.lang]['word']
        srcdir = os.path.realpath(os.curdir) + os.sep + guk + os.sep + 'pdf' + os.sep
        picfile =  name + '.pdf'
        srcfile = srcdir+picfile
        dstfile = self.tempdir+picfile
        if os.path.isfile(srcfile) :
          shutil.copyfile(srcfile, dstfile)
          self.annotate(dstfile, word, trans, prof[0], guk)
        else :
          print 'Cannot find file', picfile

  def concatPdfs(self) :
    print 'x'
    finalpdf = 'guk-%s-%s.pdf' % (self.lang, self.today)
    finalfile = os.path.realpath(os.curdir) + os.sep + finalpdf
    outputpdf = PdfFileWriter()

    keys = self.inversedata.keys()
    keys.sort()
    for f in keys :
      singlepdf = self.inversedata[f] + '-new.pdf'
      singlefullpdf = self.tempdir + singlepdf
      pdff = file(singlefullpdf, 'rb')
      px = PdfFileReader(pdff)
      p1 = px.getPage(0)
      outputpdf.addPage(p1)

    outputStream = file(finalfile, 'wb')
    outputpdf.write(outputStream)
    outputStream.close()

  def tearDown(self) :
    if os.path.isdir(self.tempdir) and not self.debug : shutil.rmtree(self.tempdir)

  def checkConsistency(self):
    print len(self.data.keys())
    gukdict = {'guk1': 0, 'guk2': 0, 'guk3': 0}
    langs = ['dt','fr','en']
    langdicts = {'dt': [], 'fr': [], 'en': []}
    for f in self.data.keys() :
      guk = self.data[f]['guk']
      for l in langs :
        name = self.data[f][l]['word']
        if not name in langdicts[l] : langdicts[l].append(name)
        else : print '%s double, %s' % (name, guk)
      gukdict[guk] += 1
      fi = os.path.realpath(os.curdir)+os.sep+guk+os.sep+'pdf'+os.sep+f+'.pdf'
      if not os.path.isfile(fi) : print fi, 'NOT OK'
    print gukdict
      
  
  def run(self) :
    self.prepareWork()
    for l in self.langs :
      self.inversedata = {}
      self.lang = l
      self.producePictures()
      self.concatPdfs()
    self.tearDown()
#    self.checkConsistency()
    


if __name__ == '__main__' : guk().run()
