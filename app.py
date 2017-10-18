
# -*- coding: utf-8 -*-#


# verzija sa slanjem maila, završiti help prozoze, qr code
'''
KB 30.08.2017.:
    * testirano je slanje maila iz aplikacije i radi dobro
'''
'''
MK 17.10.2017.:
    * riješen bug sa 'unos_lista' kod izmjene kolegija, pritiskom na 'odustani' brišu se elementi Liste
'''
'''
MK 18.10.2017.:
    * na tabu "Politehnika" u polju "Profesor" prikazuje se nul-ti element login_liste (ime trenutno ulogiranog profesora)
'''


import wx
import wx.grid
import sqlite3
import smtplib
from email.mime.text import MIMEText

conn = sqlite3.connect("MarkoKauzlaric.db")
c = conn.cursor()

# Liste

unos_lista = []

login_lista = []


# Provjere

def val_obavezan(s):
    if len(s) == 0:
        return 0
    else:
        return 1


def val_digit(d):
    if not all(e.isdigit() for e in d):
        return 0
    else:
        return 1


def val_jmbag(jb):
    if len(jb) <> 10:
        return 0
    elif not all(elem.isdigit() for elem in jb):
        return 0
    else:
        return 1


def val_student(st):
    if any(elem.isdigit() for elem in st):
        return 0
    elif len(st) == 0:
        return 0
    else:
        return 1


# Tablice

class unos_grid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1, size=(320, 420), pos=(25, 25))

        self.CreateGrid(20, 4)  # stvaramo tablicu željenih dimenzija
        self.RowLabelSize = 30  # velićina polja broja reda
        self.ColLabelSize = 40  # velićina polja imena stupca

        self.SetColLabelValue(0, u'Šifra')
        self.SetColLabelValue(1, 'Naziv')
        self.SetColLabelValue(2, 'ECTS')
        self.SetColLabelValue(3, "")

        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())

        self.SetColAttr(3, attr)
        self.SetColSize(3, 20)

        self.SetColSize(0, 80)
        self.SetColSize(1, 140)
        self.SetColSize(2, 50)
        self.SetColSize(3, 20)

        self.PuniPodatke()

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onMouse)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)
        self.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)

    def onMouse(self, evt):
        if evt.Col == 3:
            wx.CallLater(100, self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        self.cb.Value = not self.cb.Value
        self.afterCheckBox(self.cb.Value)

    def onCellSelected(self, evt):
        if evt.Col == 3:
            wx.CallAfter(self.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self, evt):
        if evt.Col == 3:
            self.cb = evt.Control
            self.cb.WindowStyle |= wx.WANTS_CHARS
            self.cb.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
            self.cb.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        evt.Skip()

    def onKeyDown(self, evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.DisableCellEditControl()
                self.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.GridCursorRow < (self.NumberRows - 1):
                self.DisableCellEditControl()
                self.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.GridCursorCol > 0:
                self.DisableCellEditControl()
                self.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.GridCursorCol < (self.NumberCols - 1):
                self.DisableCellEditControl()
                self.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self, evt):
        self.afterCheckBox(evt.IsChecked())

    def afterCheckBox(self, isChecked):
        if isChecked == True:
            if self.GetCellValue(self.GridCursorRow, 0) <> "":
                unos_lista.append([self.GetCellValue(self.GridCursorRow, 0),
                                   self.GetCellValue(self.GridCursorRow, 1),
                                   self.GetCellValue(self.GridCursorRow, 2)])

        elif isChecked == False:
            if self.GetCellValue(self.GridCursorRow, 0) <> "":
                unos_lista.remove([self.GetCellValue(self.GridCursorRow, 0),
                                   self.GetCellValue(self.GridCursorRow, 1),
                                   self.GetCellValue(self.GridCursorRow, 2)])

    def PuniPodatke(self):
        self.ClearGrid()
        for el in login_lista:
            c.execute("SELECT * FROM kol_nos WHERE ŠifraProf = ?", (el[0][1]))
            rows_unos = c.fetchall()
            r = 0
            for e in rows_unos:
                self.SetCellValue(r, 0, unicode(e[1]))
                self.SetCellValue(r, 1, unicode(e[0]))
                self.SetCellValue(r, 2, unicode(e[2]))
                r += 1


class evid_grid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1, size=(470, 420), pos=(35, 25))

        self.CreateGrid(20, 5)
        self.RowLabelSize = 30
        self.ColLabelSize = 40

        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.SetColAttr(4, attr)
        self.SetColSize(4, 20)

        self.SetColLabelValue(0, 'Godina')
        self.SetColLabelValue(1, 'Jmbag')
        self.SetColLabelValue(2, 'Ime i prezime')
        self.SetColLabelValue(3, "Kolegij")
        self.SetColLabelValue(4, "")

        self.SetColSize(0, 50)
        self.SetColSize(1, 90)
        self.SetColSize(2, 130)
        self.SetColSize(3, 150)

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onMouse)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)
        self.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)

        self.PuniPodatkeStudenti()

    def onMouse(self, evt):
        if evt.Col == 4:
            wx.CallLater(100, self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        self.cb.Value = not self.cb.Value
        self.afterCheckBox(self.cb.Value)

    def onCellSelected(self, evt):
        if evt.Col == 4:
            wx.CallAfter(self.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self, evt):
        if evt.Col == 4:
            self.cb = evt.Control
            self.cb.WindowStyle |= wx.WANTS_CHARS
            self.cb.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
            self.cb.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        evt.Skip()

    def onKeyDown(self, evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.DisableCellEditControl()
                self.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.GridCursorRow < (self.NumberRows - 1):
                self.DisableCellEditControl()
                self.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.GridCursorCol > 0:
                self.DisableCellEditControl()
                self.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.GridCursorCol < (self.NumberCols - 1):
                self.DisableCellEditControl()
                self.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self, evt):
        self.afterCheckBox(evt.IsChecked())

    def afterCheckBox(self, isChecked):
        if isChecked == True:
            if self.GetCellValue(self.GridCursorRow, 0) <> "":
                unos_lista.append([self.GetCellValue(self.GridCursorRow, 0),
                                   self.GetCellValue(self.GridCursorRow, 1),
                                   self.GetCellValue(self.GridCursorRow, 2),
                                   self.GetCellValue(self.GridCursorRow, 3)])

        elif isChecked == False:
            if self.GetCellValue(self.GridCursorRow, 0) <> "":
                unos_lista.remove([self.GetCellValue(self.GridCursorRow, 0),
                                   self.GetCellValue(self.GridCursorRow, 1),
                                   self.GetCellValue(self.GridCursorRow, 2),
                                   self.GetCellValue(self.GridCursorRow, 3)])

    def PuniPodatkeStudenti(self):
        for el in login_lista:

            self.ClearGrid()
            c.execute("SELECT * FROM st_kol_nos WHERE ŠifraProf = ?", (unicode(el[0][1]),))
            rows_unos = c.fetchall()
            r = 0
            for e in rows_unos:
                self.SetCellValue(r, 0, unicode(e[3]))
                self.SetCellValue(r, 1, unicode(e[1]))
                self.SetCellValue(r, 2, unicode(e[2]))
                self.SetCellValue(r, 3, unicode(e[5]))
                r += 1


class prisutstvo_grid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1, size=(550, 420), pos=(35, 25))

        self.CreateGrid(20, 6)  # stvaramo tablicu željenih dimenzija
        self.RowLabelSize = 30  # velićina polja broja reda
        self.ColLabelSize = 40  # velićina polja imena stupca

        self.SetColLabelValue(0, u'Šifra')
        self.SetColLabelValue(1, 'Naziv')
        self.SetColLabelValue(2, 'Jmbag')
        self.SetColLabelValue(3, 'Ime i prezime')
        self.SetColLabelValue(4, 'Datum')
        self.SetColLabelValue(5, "")

        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())

        self.SetColAttr(5, attr)
        self.SetColSize(5, 20)

        self.SetColSize(0, 80)
        self.SetColSize(1, 140)
        self.SetColSize(2, 70)
        self.SetColSize(3, 130)
        self.SetColSize(4, 80)
        self.SetColSize(5, 20)

        self.PuniPodatkeEvid()

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onMouse)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)
        self.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)

    def onMouse(self, evt):
        if evt.Col == 5:
            wx.CallLater(100, self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        self.cb.Value = not self.cb.Value
        self.afterCheckBox(self.cb.Value)

    def onCellSelected(self, evt):
        if evt.Col == 5:
            wx.CallAfter(self.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self, evt):
        if evt.Col == 5:
            self.cb = evt.Control
            self.cb.WindowStyle |= wx.WANTS_CHARS
            self.cb.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
            self.cb.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        evt.Skip()

    def onKeyDown(self, evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.DisableCellEditControl()
                self.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.GridCursorRow < (self.NumberRows - 1):
                self.DisableCellEditControl()
                self.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.GridCursorCol > 0:
                self.DisableCellEditControl()
                self.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.GridCursorCol < (self.NumberCols - 1):
                self.DisableCellEditControl()
                self.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self, evt):
        self.afterCheckBox(evt.IsChecked())

    def afterCheckBox(self, isChecked):
        if isChecked == True:
            if self.GetCellValue(self.GridCursorRow, 0) <> "":
                unos_lista.append([self.GetCellValue(self.GridCursorRow, 0),
                                   self.GetCellValue(self.GridCursorRow, 1),
                                   self.GetCellValue(self.GridCursorRow, 2),
                                   self.GetCellValue(self.GridCursorRow, 3),
                                   self.GetCellValue(self.GridCursorRow, 4)])

        else:
            if self.GetCellValue(self.GridCursorRow, 0) <> "":
                unos_lista.remove([self.GetCellValue(self.GridCursorRow, 0),
                                   self.GetCellValue(self.GridCursorRow, 1),
                                   self.GetCellValue(self.GridCursorRow, 2),
                                   self.GetCellValue(self.GridCursorRow, 3),
                                   self.GetCellValue(self.GridCursorRow, 4)])

    def PuniPodatkeEvid(self):
        self.ClearGrid()
        for el in login_lista:
            c.execute("SELECT * FROM pr_ko_st WHERE ŠifraProf = ?", (el[0][1]), )
            rows_unos = c.fetchall()
            r = 0
            for el in rows_unos:
                self.SetCellValue(r, 0, unicode(el[2]))
                self.SetCellValue(r, 1, unicode(el[3]))
                self.SetCellValue(r, 2, unicode(el[5]))
                self.SetCellValue(r, 3, unicode(el[6]))
                self.SetCellValue(r, 4, unicode(el[7]))
                r += 1


# Tabovi

class tab_unos(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.panel = wx.Panel(self)
        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_main_win.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(850, 600))

        self.grd = unos_grid(self.slika)
        button = wx.Button(self.slika, label="Unos novog kolegija", pos=(430, 50), size=(150, 70))
        button1 = wx.Button(self.slika, label=u"Briši", pos=(430, 240), size=(150, 70))
        button2 = wx.Button(self.slika, label=u"Izmjeni podatke", pos=(430, 145), size=(150, 70))
        button4 = wx.Button(self.slika, label=u"Filtriraj", pos=(345, 449), size=(55, 25))
        button5 = wx.Button(self.slika, label=u"Help", pos=(5, 570), size=(55, 25))

        self.Bind(wx.EVT_BUTTON, self.butt_brisi, button1)
        self.Bind(wx.EVT_BUTTON, self.unos, button)
        self.Bind(wx.EVT_BUTTON, self.izmjeni, button2)
        self.Bind(wx.EVT_BUTTON, self.filter, button4)
        self.Bind(wx.EVT_BUTTON, self.help, button5)

        self.sifra_fText = wx.TextCtrl(self.slika, -1, "", size=(80, -1), pos=(55, 450))
        # self.sifra_fText.SetValue("%")

        self.naziv_fText = wx.TextCtrl(self.slika, -1, "", size=(140, -1), pos=(137, 450))
        # self.naziv_fText.SetValue("%")

        self.ects_fText = wx.TextCtrl(self.slika, -1, "", size=(50, -1), pos=(278, 450))
        # self.ects_fText.SetValue("%")

    def help(self, event):
        frame = help_frame(self)
        frame.Show()

    def filter(self, event):
        for el in login_lista:
            # self.grd.ClearGrid()
            c.execute(
                "SELECT * FROM kol_nos WHERE Šifra LIKE ? AND Naziv LIKE ? AND ECTS LIKE ? AND ŠifraProf LIKE ? ORDER BY ECTS",
                ("%" + self.sifra_fText.GetValue() + "%", "%" + self.naziv_fText.GetValue() + "%",
                 "%" + self.ects_fText.GetValue() + "%", el[0][1]))
            # c.execute("select * from Kolegiji" + "where Šifra = ?",(self.sifra_fText.GetValue(),self.naziv_fText.GetValue(),self.ects_fText.GetValue))
            # c.execute("select * from Kolegiji where Šifra like ? and Naziv like ? and ECTS like ?",(self.sifra_fText.GetValue(),self.naziv_fText.GetValue(),self.ects_fText.GetValue()))
            self.grd.ClearGrid()
            rows_unos = c.fetchall()
            r = 0
            for el in rows_unos:
                self.grd.SetCellValue(r, 0, str(el[1]))
                self.grd.SetCellValue(r, 1, str(el[0]))
                self.grd.SetCellValue(r, 2, str(el[2]))
                r += 1

            self.sifra_fText.SetValue("")
            self.naziv_fText.SetValue("")
            self.ects_fText.SetValue("")

    def butt_brisi(self, event):
        if len(unos_lista) == 0:
            message = wx.MessageDialog(self, u"Potrebno je odabrati kolegij koji želite izbrisati!",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        else:
            message = wx.MessageDialog(self, u"Jeste li sigurni da želite obrisati odabrane kolegije iz baze?",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            if res == wx.ID_OK:
                for e in unos_lista:
                    c.execute("SELECT Id FROM Kolegiji WHERE Šifra = ?", (e[0],))
                    rows_id = c.fetchall()

                    c.execute("DELETE FROM Kol_Nositelj WHERE Id_kolegija = ?", (rows_id[0][0],))
                    c.execute("DELETE FROM Kolegiji WHERE Id = ?", (rows_id[0][0],))
                    conn.commit()

            else:
                message.Destroy()

            self.grd.PuniPodatke()

    def unos(self, event):
        frame = unoskol_frame(self)
        frame.Show()

    def izmjeni(self, event):
        if len(unos_lista) == 0:
            message = wx.MessageDialog(self, u"Potrebno je odabrati kolegij čije podatke želite izmjeniti",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        elif len(unos_lista) > 1:
            message = wx.MessageDialog(self, u"Izmjena podataka moguća je samo za jedan po jedan kolegij!",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
        else:
            frame = izmjkol_frame(self)
            frame.Show()
        self.grd.PuniPodatke()

class tab_evid(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_main_win.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(850, 600))

        self.grd = evid_grid(self.slika)

        button = wx.Button(self.slika, label="Unesi studenta", pos=(540, 110), size=(150, 70))
        button1 = wx.Button(self.slika, label=u"Briši", pos=(540, 310), size=(150, 70))
        button2 = wx.Button(self.slika, label="Izmjeni podatke", pos=(540, 210), size=(150, 70))
        button4 = wx.Button(self.slika, label=u"Filtriraj", pos=(500, 449), size=(55, 25))
        button5 = wx.Button(self.slika, label=u"Help", pos=(5, 570), size=(55, 25))
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        grdsizer = wx.BoxSizer(wx.VERTICAL)

        self.Bind(wx.EVT_BUTTON, self.butt_brisi, button1)
        self.Bind(wx.EVT_BUTTON, self.unosst, button)
        self.Bind(wx.EVT_BUTTON, self.filter_s, button4)
        self.Bind(wx.EVT_BUTTON, self.izmjst, button2)
        self.Bind(wx.EVT_BUTTON, self.help, button5)

        self.godina_fText = wx.TextCtrl(self.slika, -1, "", size=(50, -1), pos=(63, 450))
        # self.godina_fText.SetValue("%")

        self.jmbag_fText = wx.TextCtrl(self.slika, -1, "", size=(90, -1), pos=(115, 450))
        # self.jmbag_fText.SetValue("%")

        self.imeprezime_fText = wx.TextCtrl(self.slika, -1, "", size=(130, -1), pos=(207, 450))

        self.kol_fText = wx.TextCtrl(self.slika, -1, "", size=(150, -1), pos=(340, 450))

    def filter_s(self, event):
        for el in login_lista:
            c.execute(
                "SELECT * FROM st_kol_nos WHERE Godina LIKE ? AND Jmbag LIKE ? AND ime_prezime LIKE ? AND ŠifraProf LIKE ? AND Naziv LIKE ? ORDER BY Godina",
                ("%" + self.godina_fText.GetValue() + "%", "%" + self.jmbag_fText.GetValue() + "%",
                 "%" + self.imeprezime_fText.GetValue() + "%", el[0][1], "%" + self.kol_fText.GetValue() + "%"))
            # c.execute("select * from Kolegiji" + "where Šifra = ?",(self.sifra_fText.GetValue(),self.naziv_fText.GetValue(),self.ects_fText.GetValue))
            # c.execute("select * from Kolegiji where Šifra like ? and Naziv like ? and ECTS like ?",(self.sifra_fText.GetValue(),self.naziv_fText.GetValue(),self.ects_fText.GetValue()))
            self.grd.ClearGrid()
            rows_unos = c.fetchall()
            r = 0
            for el in rows_unos:
                self.grd.SetCellValue(r, 0, unicode(el[3]))
                self.grd.SetCellValue(r, 1, unicode(el[1]))
                self.grd.SetCellValue(r, 2, unicode(el[2]))
                self.grd.SetCellValue(r, 3, unicode(el[5]))
                r += 1

            self.godina_fText.SetValue("")
            self.jmbag_fText.SetValue("")
            self.imeprezime_fText.SetValue("")
            self.kol_fText.SetValue("")

    def butt_brisi(self, event):
        message = wx.MessageDialog(self, u"Jeste li sigurni da želite obrisati odabrane studente iz baze?",
                                   style=wx.OK | wx.CANCEL)
        res = message.ShowModal()
        if res == wx.ID_OK:
            for e in unos_lista:
                c.execute("SELECT Id FROM studenti WHERE JMBAG = ?", (e[1],))
                rows_s = c.fetchall()
                c.execute("SELECT Id FROM Kolegiji WHERE Naziv = ?", (e[3],))
                rows_k = c.fetchall()

                c.execute("DELETE FROM st_kolegiji WHERE Id_st = ? AND Id_kol = ?",
                          (unicode(rows_s[0][0]), unicode(rows_k[0][0])))
                c.execute("DELETE FROM Studenti WHERE JMBAG=?", (e[1],))
                conn.commit()

                self.grd.PuniPodatkeStudenti()

            del unos_lista[:]
        else:
            message.Destroy()

    def unosst(self, event):
        frame = unosst_frame(self)
        frame.Show()

    def izmjst(self, event):
        if len(unos_lista) == 0:
            message = wx.MessageDialog(self, u"Potrebno je odabrati studenta čije podatke želite izmjeniti",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        elif len(unos_lista) > 1:
            message = wx.MessageDialog(self, u"Izmjena podataka moguća je samo za jednog po jednog studenta!",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
        else:
            frame = izmjst_frame(self)
            frame.Show()

    def help(self, event):
        frame = help_frame(self)
        frame.Show()


class tab_evidencija(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_main_win.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(850, 600))

        self.grd = prisutstvo_grid(self.slika)

        self.sifra_fText = wx.TextCtrl(self.slika, -1, "", size=(78, -1), pos=(63, 450))

        self.naziv_fText = wx.TextCtrl(self.slika, -1, "", size=(140, -1), pos=(143, 450))

        self.jmbag_fText = wx.TextCtrl(self.slika, -1, "", size=(70, -1), pos=(285, 450))

        self.imeiprezime_fText = wx.TextCtrl(self.slika, -1, "", size=(130, -1), pos=(356, 450))

        self.datum_fText = wx.TextCtrl(self.slika, -1, "", size=(78, -1), pos=(488, 450))

        # datum_evLabel = wx.StaticText(self, -1, "Ukupno:",pos=(440,485))
        # self.datum_evText = wx.TextCtrl(self, -1, "", size=(78, -1),pos=(488,483))


        button2 = wx.Button(self.slika, label=u"Obriši prisustvo", pos=(640, 120), size=(120, 70))
        button4 = wx.Button(self.slika, label=u"Filtriraj", pos=(290, 475), size=(55, 25))
        button3 = wx.Button(self.slika, label=u"Unesi prisutstvo", pos=(640, 220), size=(120, 70))
        button5 = wx.Button(self.slika, label=u"Help", pos=(5, 570), size=(55, 25))
        self.Bind(wx.EVT_BUTTON, self.butt_brisi, button2)
        self.Bind(wx.EVT_BUTTON, self.evid, button3)
        self.Bind(wx.EVT_BUTTON, self.filter_ev, button4)
        self.Bind(wx.EVT_BUTTON, self.help, button5)

    def help(self, event):
        frame = help_frame(self)
        frame.Show()

    def butt_brisi(self, event):
        message = wx.MessageDialog(self, u"Jeste li sigurni da želite obrisati odabrano prisustvo iz baze?",
                                   style=wx.OK | wx.CANCEL)
        res = message.ShowModal()
        print unos_lista
        if res == wx.ID_OK:
            for e in unos_lista:
                c.execute(
                    "SELECT Prisustvo.id_kol FROM Prisustvo, Kolegiji, Studenti WHERE Prisustvo.id_kol = Kolegiji.Id AND Prisustvo.id_st = Studenti.Id AND Šifra = ? AND Jmbag = ? AND Datum = ?",
                    (e[0], e[2], e[4]))
                r_sif = c.fetchall()

                c.execute(
                    "SELECT Prisustvo.id_st FROM Prisustvo, Kolegiji, Studenti WHERE Prisustvo.id_st = Studenti.Id AND Prisustvo.id_kol = Kolegiji.Id AND Šifra = ? AND Jmbag = ? AND Datum = ?",
                    ((e[0]), e[2], e[4]))
                r_stu = c.fetchall()

                c.execute("DELETE FROM Prisustvo WHERE id_kol = ? AND id_st = ? AND Datum = ?",
                          (unicode(r_sif[0][0]), unicode(r_stu[0][0]), unicode(e[4])))
                conn.commit()
                del unos_lista[:]

                self.grd.PuniPodatkeEvid()
        else:
            message.Destroy()

    def evid(self, event):
        frame = evidencija_frame(self)
        frame.Show()

    def filter_ev(self, event):
        for e in login_lista:
            c.execute(
                "SELECT Šifra, Naziv, Jmbag, ime_prezime, Datum FROM pr_ko_st WHERE Šifra LIKE ? AND Naziv LIKE ? AND Jmbag LIKE ? AND Ime_prezime LIKE ? AND Datum LIKE ? AND ŠifraProf LIKE ?",
                ("%" + self.sifra_fText.GetValue() + "%", "%" + self.naziv_fText.GetValue() + "%",
                 "%" + self.jmbag_fText.GetValue() + "%", "%" + self.imeiprezime_fText.GetValue() + "%",
                 "%" + self.datum_fText.GetValue() + "%", e[0][1]))
            self.grd.ClearGrid()
            rows_unos = c.fetchall()
            r = 0
            for el in rows_unos:
                self.grd.SetCellValue(r, 0, unicode(el[0]))
                self.grd.SetCellValue(r, 1, unicode(el[1]))
                self.grd.SetCellValue(r, 2, unicode(el[2]))
                self.grd.SetCellValue(r, 3, unicode(el[3]))
                self.grd.SetCellValue(r, 4, unicode(el[4]))
                r += 1

            self.sifra_fText.SetValue("")
            self.naziv_fText.SetValue("")
            self.jmbag_fText.SetValue("")
            self.imeiprezime_fText.SetValue("")
            self.datum_fText.SetValue("")


class tab_poli(wx.Panel):
    def __init__(self, Parent):
        wx.Panel.__init__(self, Parent)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_politab.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(850, 600))

        self.prijedlogText = wx.TextCtrl(self.slika, -1, "", size=(380, 200), pos=(45, 100), style=wx.TE_MULTILINE)

        self.profLabel = wx.TextCtrl(self.slika, -1, "", pos=(110, 70))

        for e in login_lista:
            self.profLabel.SetValue(e[0][0])

        button = wx.Button(self.slika, label=u"Pošalji", pos=(430, 100), size=(80, 40))
        self.Bind(wx.EVT_BUTTON, self.send_mail, button)

        button5 = wx.Button(self.slika, label=u"Help", pos=(5, 570), size=(55, 25))
        self.Bind(wx.EVT_BUTTON, self.help, button5)

    def help(self, event):
        frame = help_frame(self)
        frame.Show()

    def send_mail(self, event):

        content = MIMEText(self.prijedlogText.GetValue(), 'plain', 'utf-8')  # ascii decoding

        try:
            mail = smtplib.SMTP('smtp.gmail.com', 587)  # gmail domena/port
            mail.ehlo()
            mail.starttls()
            mail.login('poliaplikacija@gmail.com', 'Politehnika1')  # sender (adress/pass)
            mail.sendmail('poliaplikacija@gmail.com', ['kauzlaricmarko@yahoo.com.hr', 'kblaskovi@politehnika-pula.hr'],
                          content.as_string())  # sender, receivers[list], content(string)
            mail.close()
            message = wx.MessageDialog(self, u"Hvala na prijedlogu, poruka je uspješno poslana",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.prijedlogText.SetValue("")


        except smtplib.SMTPException:
            message = wx.MessageDialog(self, u"Greška! Poruka nije poslana.", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()


# Prozori za unos

class unosst_frame(wx.Frame):
    def __init__(self, Parent):
        wx.Frame.__init__(self, Parent, -1, title="Unos studenta", size=(375, 350))
        panel = wx.Panel(self)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_st.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))

        button = wx.Button(self.slika, label="Spremi", pos=(70, 240), size=(90, 50))
        button1 = wx.Button(self.slika, label=u"Odustani", pos=(200, 240), size=(90, 50))

        self.Bind(wx.EVT_BUTTON, self.odustani, button1)
        self.Bind(wx.EVT_BUTTON, self.spremi, button)

        # sifraLabel = wx.StaticText(self.slika, -1, u"Godina:",pos=(20,30))
        self.godinaText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 103))

        # sifraLabel = wx.StaticText(self.slika, -1, u"Jmbag:",pos=(20,60))
        self.jmbagText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 137))

        # nazivLabel = wx.StaticText(self.slika, -1, "Ime i prezime:",pos=(20,90))
        self.imeText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(150, 167))

        self.kolText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 197))

    def spremi(self, event):

        if val_obavezan(self.jmbagText.GetValue()) == 0 or val_digit(self.jmbagText.GetValue()) == 0 or val_jmbag(
                self.jmbagText.GetValue()) == 0:
            message = wx.MessageDialog(self,
                                       u"Jmbag broj je obavezan, mora imati 10 zanamenki, i sastoji se samo od brojeva!",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.jmbagText.SetValue("")


        elif val_obavezan(self.imeText.GetValue()) == 0 or val_student(self.imeText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Ime studenta je obavezno", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.imeText.SetValue("")

        elif val_obavezan(self.godinaText.GetValue()) == 0 or val_digit(self.godinaText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Godina studija je obavezna", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.godinaText.SetValue("")

        else:
            c.execute("SELECT Id FROM Kolegiji WHERE Naziv = ?", (self.kolText.GetValue(),))
            rows_k = c.fetchall()
            print rows_k

            if len(rows_k) == 0:
                message = wx.MessageDialog(self, u"Nepostojeći kolegij!", style=wx.OK | wx.CANCEL)
                res = message.ShowModal()
                message.Destroy()
                self.kolText.SetValue("")

            else:

                c.execute("INSERT INTO Studenti VALUES(NULL,?,?,?)",
                          (self.godinaText.GetValue(), self.jmbagText.GetValue(), self.imeText.GetValue()))
                conn.commit()

                c.execute("SELECT Id FROM Studenti WHERE jmbag = ?", (self.jmbagText.GetValue(),))
                rows_s = c.fetchall()

                c.execute("INSERT INTO st_kolegiji VALUES(NULL,?,?)", (unicode(rows_s[0][0]), unicode(rows_k[0][0])))
                conn.commit()

                message = wx.MessageDialog(self, u"Uspješno unešeno", style=wx.OK)
                res = message.ShowModal()

                self.godinaText.SetValue("")
                self.jmbagText.SetValue("")
                self.imeText.SetValue("")
                self.kolText.SetValue("")

        self.GetParent().grd.PuniPodatkeStudenti()

    def odustani(self, event):
        self.Close(True)


class unoskol_frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="Unos kolegija", size=(375, 350))
        panel = wx.Panel(self)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_kol.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))

        button = wx.Button(self.slika, label="Spremi", pos=(70, 220), size=(90, 50))
        button1 = wx.Button(self.slika, label=u"Odustani", pos=(200, 220), size=(90, 50))

        self.Bind(wx.EVT_BUTTON, self.odustani, button1)
        self.Bind(wx.EVT_BUTTON, self.spremi, button)

        # sifraLabel = wx.StaticText(panel, -1, u"Šifra:",pos=(50,40))
        self.nazivText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 103))

        # nazivLabel = wx.StaticText(panel, -1, "Naziv:",pos=(50,70))
        self.sifraText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 137))

        # ectsLabel = wx.StaticText(panel, -1, "Ects:",pos=(50,100))
        self.ectsText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 167))

    def spremi(self, event):

        if val_obavezan(self.sifraText.GetValue()) == 0 or val_digit(self.sifraText.GetValue()) == 0:
            message = wx.MessageDialog(self, u"Unos šifre je obavezan i mora sadržavati samo brojeve",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.sifraText.SetValue("")


        elif val_obavezan(self.nazivText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Unos naziva kolegija je obavezan", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.nazivText.SetValue("")



        elif val_obavezan(self.ectsText.GetValue()) == 0 or val_digit(self.ectsText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Unos ECTS bodoa je obavezan", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.ectsText.SetValue("")


        else:

            for el in login_lista:
                c.execute("INSERT INTO Kolegiji VALUES(NULL,?,?,?)",
                          (self.sifraText.GetValue(), self.nazivText.GetValue(), self.ectsText.GetValue()))

                c.execute("SELECT * FROM Kolegiji WHERE Šifra = ?", (self.sifraText.GetValue(),))
                rows_kol = c.fetchall()

                c.execute("SELECT Id FROM Nositelji WHERE ŠifraProf = ?", (el[0][1]), )
                rows_k = c.fetchall()

                c.execute("INSERT INTO Kol_nositelj VALUES(NULL, ?, ?)",
                          (unicode(rows_kol[0][0]), unicode(rows_k[0][0])))
                conn.commit()

                message = wx.MessageDialog(self, u"Uspješno unešeno", style=wx.OK)
                res = message.ShowModal()

                self.sifraText.SetValue("")
                self.nazivText.SetValue("")
                self.ectsText.SetValue("")

        self.GetParent().grd.PuniPodatke()

    def odustani(self, event):
        self.Close(True)


class izmjkol_frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="Unos kolegija", size=(375, 350))
        panel = wx.Panel(self)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_kol.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))

        button = wx.Button(self.slika, label="Izmjeni", pos=(70, 220), size=(90, 50))
        button1 = wx.Button(self.slika, label=u"Odustani", pos=(200, 220), size=(90, 50))

        self.Bind(wx.EVT_BUTTON, self.odustani, button1)
        self.Bind(wx.EVT_BUTTON, self.izmjeni, button)

        # sifraLabel = wx.StaticText(panel, -1, u"Šifra:",pos=(50,40))
        self.nazivText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 103))
        self.nazivText.SetValue(unos_lista[0][1])

        # nazivLabel = wx.StaticText(panel, -1, "Naziv:",pos=(50,70))
        self.sifraText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 137))
        self.sifraText.SetValue(unos_lista[0][0])

        # ectsLabel = wx.StaticText(panel, -1, "Ects:",pos=(50,100))
        self.ectsText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 167))
        self.ectsText.SetValue(unos_lista[0][2])

    def izmjeni(self, event):

        if val_obavezan(self.sifraText.GetValue()) == 0 or val_digit(self.sifraText.GetValue()) == 0:
            message = wx.MessageDialog(self, u"Unes šifre je obavezan i mora sadržavati samo brojeve",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        elif val_obavezan(self.nazivText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Unos naziva kolegija je obavezan", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        elif val_obavezan(self.ectsText.GetValue()) == 0 or val_digit(self.ectsText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Unos ECTS bodova je obavezan", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        else:
            for e in unos_lista:
                c.execute("UPDATE Kolegiji SET Šifra = ?, Naziv = ?, ECTS = ? WHERE Šifra = ?",
                          (self.sifraText.GetValue(), self.nazivText.GetValue(), self.ectsText.GetValue(), e[0]))
                conn.commit()
                message = wx.MessageDialog(self, u"Uspješno unešeno", style=wx.OK)
                res = message.ShowModal()
                del unos_lista[:]

                self.sifraText.SetValue("")
                self.nazivText.SetValue("")
                self.ectsText.SetValue("")

                self.Close(True)

        self.GetParent().grd.PuniPodatke()

    def odustani(self, event):
        del unos_lista[:]
        self.Close(True)


class izmjst_frame(wx.Frame):
    def __init__(self, Parent):
        wx.Frame.__init__(self, Parent, -1, title="Izmjena podataka", size=(375, 350))
        panel = wx.Panel(self)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_st_izmj.jpg", wx.BITMAP_TYPE_ANY),
                                     pos=wx.Point(0, 0), size=(366, 338))

        button = wx.Button(self.slika, label="Spremi", pos=(70, 220), size=(90, 50))
        button1 = wx.Button(self.slika, label=u"Odustani", pos=(200, 220), size=(90, 50))

        self.Bind(wx.EVT_BUTTON, self.odustani, button1)
        self.Bind(wx.EVT_BUTTON, self.spremi, button)

        # sifraLabel = wx.StaticText(panel, -1, u"Godina:",pos=(20,30))
        self.godinaText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 103))
        self.godinaText.SetValue(unos_lista[0][0])

        # sifraLabel = wx.StaticText(panel, -1, u"Jmbag:",pos=(20,60))
        self.jmbagText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 137))
        self.jmbagText.SetValue(unos_lista[0][1])

        # nazivLabel = wx.StaticText(panel, -1, "Ime i prezime:",pos=(20,90))
        self.imeText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(150, 167))
        self.imeText.SetValue(unos_lista[0][2])

    def spremi(self, event):

        if val_obavezan(self.jmbagText.GetValue()) == 0 or val_digit(self.jmbagText.GetValue()) == 0 or val_jmbag(
                self.jmbagText.GetValue()) == 0:
            message = wx.MessageDialog(self,
                                       u"Unos jmbag broja je obavezan, mora imati 10 znamenki i sadrži samo brojeve",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()


        elif val_obavezan(self.imeText.GetValue()) == 0 or val_student(self.imeText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Ime studenta je obavezno", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        elif val_obavezan(self.godinaText.GetValue()) == 0 or val_digit(self.godinaText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Godina studija je obavezna", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()

        else:
            for e in unos_lista:
                c.execute("UPDATE Studenti SET Godina = ?, Jmbag = ?, ime_prezime = ? WHERE Jmbag = ?",
                          (self.godinaText.GetValue(), self.jmbagText.GetValue(), self.imeText.GetValue(), e[1]))
                conn.commit()
                message = wx.MessageDialog(self, u"Uspješno unešeno", style=wx.OK)
                res = message.ShowModal()

                self.jmbagText.SetValue("")
                self.imeText.SetValue("")
                self.godinaText.SetValue("")

                del unos_lista[:]

                self.Close(True)

        self.GetParent().grd.PuniPodatkeStudenti()

    def odustani(self, event):
        self.Close(True)


class evidencija_frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="Unos kolegija", size=(375, 350))
        panel = wx.Panel(self)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_evid.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))

        button = wx.Button(self.slika, label="Unesi", pos=(70, 220), size=(90, 50))
        button1 = wx.Button(self.slika, label=u"Odustani", pos=(200, 220), size=(90, 50))

        self.Bind(wx.EVT_BUTTON, self.odustani, button1)
        self.Bind(wx.EVT_BUTTON, self.spremi, button)

        # sifraLabel = wx.StaticText(self.slika, -1, u"Šifra:",pos=(50,50))
        self.sifraText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 103))

        # jmbagLabel = wx.StaticText(self.slika, -1, "Jmbag:",pos=(50,100))
        self.jmbagText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 137))

        # datumLabel = wx.StaticText(self.slika, -1, "Datum:",pos=(50,150))
        self.datumText = wx.TextCtrl(self.slika, -1, "", size=(175, -1), pos=(103, 167))

    def odustani(self, event):
        self.Close(True)

    def spremi(self, event):

        if val_obavezan(self.jmbagText.GetValue()) == 0 or val_digit(self.jmbagText.GetValue()) == 0 or val_jmbag(
                self.jmbagText.GetValue()) == 0:
            message = wx.MessageDialog(self,
                                       u"Unos jmbag broja je obavezan, mora imati 10 znamenki i sadrži samo brojeve",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.jmbagText.SetValue("")


        elif val_obavezan(self.datumText.GetValue()) == 0:  # or val_digit(self.datumText.GetValue()) == 0:
            message = wx.MessageDialog(self, "Unos datuma je obavezan", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.datumText.SetValue("")


        elif val_obavezan(self.sifraText.GetValue()) == 0 or val_digit(self.sifraText.GetValue()) == 0:
            message = wx.MessageDialog(self, u"Unos šifre je obavezan i mora sadržavati samo brojeve",
                                       style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.sifraText.SetValue("")


        else:
            c.execute("SELECT Id FROM Kolegiji WHERE Šifra = ?", (self.sifraText.GetValue(),))
            r_kol = c.fetchall()
            c.execute("SELECT Id FROM Studenti WHERE Jmbag = ?", (self.jmbagText.GetValue(),))
            r_st = c.fetchall()

            if r_kol == []:
                message = wx.MessageDialog(self, u"Nepostojeća šifra kolegija!")
                res = message.ShowModal()
                message.Destroy()
                self.sifraText.SetValue("")

            elif r_st == []:
                message = wx.MessageDialog(self, u"Nepostojeći jmbag studenta!")
                res = message.ShowModal()
                message.Destroy()
                self.jmbagText.SetValue("")

            else:
                c.execute("INSERT INTO Prisustvo VALUES(NULL,?,?,?)",
                          (str(r_kol[0][0]), str(r_st[0][0]), self.datumText.GetValue()))
                conn.commit()
                message = wx.MessageDialog(self, u"Uspješno unešeno", style=wx.OK)
                res = message.ShowModal()

                self.jmbagText.SetValue("")

            self.GetParent().grd.PuniPodatkeEvid()


class help_frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="Help", size=(380, 300))
        panel = wx.Panel(self)

        button = wx.Button(panel, label="Kolegiji", pos=(60, 200), size=(60, 30))
        button1 = wx.Button(panel, label="Studenti", pos=(120, 200), size=(60, 30))
        button2 = wx.Button(panel, label="Prisustvo", pos=(180, 200), size=(60, 30))
        button3 = wx.Button(panel, label="Politehnika", pos=(240, 200), size=(75, 30))

        self.Bind(wx.EVT_BUTTON, self.help_unos, button)
        self.Bind(wx.EVT_BUTTON, self.help_stud, button1)
        self.Bind(wx.EVT_BUTTON, self.help_prist, button2)
        self.Bind(wx.EVT_BUTTON, self.help_poli, button3)

    def help_unos(self, event):
        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_st.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))
        self.slika.Show()

    def help_stud(self, event):
        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_st.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))
        self.slika.Show()

    def help_prist(self, event):
        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_st.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))
        self.slika.Show()

    def help_poli(self, event):
        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_forma_st.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))
        self.slika.Show()


# main prozor

class main_win(wx.Frame):
    def __init__(self, ):
        wx.Frame.__init__(self, None, title="Aplikacija Politehnika", size=(870, 665))

        p = wx.Panel(self)
        tabovi = wx.Notebook(p)

        tab1 = tab_unos(tabovi)
        tab2 = tab_evid(tabovi)
        tab3 = tab_evidencija(tabovi)
        tab4 = tab_poli(tabovi)

        tabovi.AddPage(tab1, "Kolegiji")
        tabovi.AddPage(tab2, "Studenti")
        tabovi.AddPage(tab3, "Evidencija prisutstva")
        tabovi.AddPage(tab4, "Politehnika")

        sizer = wx.BoxSizer()
        sizer.Add(tabovi, 1, wx.EXPAND)
        p.SetSizer(sizer)
        sizer.Layout()

        self.Center()


class login(wx.Frame):
    def __init__(self, ):
        wx.Frame.__init__(self, None, -1, title="Aplikacija Politehnika", size=(375, 350))
        panel = wx.Panel(self, -1)

        self.slika = wx.StaticBitmap(self, -1, wx.Bitmap("app_login.jpg", wx.BITMAP_TYPE_ANY), pos=wx.Point(0, 0),
                                     size=(366, 338))

        button = wx.Button(self.slika, -1, label="Pristupi", pos=(90, 215), size=(90, 50))
        button1 = wx.Button(self.slika, -1, label=u"Odustani", pos=(190, 215), size=(90, 50))

        self.Bind(wx.EVT_BUTTON, self.odustani, button1)
        self.Bind(wx.EVT_BUTTON, self.pristupi, button)

        self.sifraText = wx.TextCtrl(self.slika, -1, "", size=(90, -1), style=wx.TE_PASSWORD)
        self.sifraText.Center()

        self.Center()

    def pristupi(self, event):

        if val_obavezan(self.sifraText.GetValue()) == 0:
            message = wx.MessageDialog(self, u"Unos šifre je obavezan!", style=wx.OK | wx.CANCEL)
            res = message.ShowModal()
            message.Destroy()
            self.sifraText.SetValue("")

        else:
            c.execute("SELECT Profesor, ŠifraProf FROM Nositelji WHERE ŠifraProf = ?", (self.sifraText.GetValue(),))
            rows_s = c.fetchall()

            if len(rows_s) == 0:
                message = wx.MessageDialog(self, u"Nepostojeći profesor!", style=wx.OK | wx.CANCEL)
                res = message.ShowModal()
                message.Destroy()

            else:
                login_lista.append(rows_s)
                print login_lista
                frame = main_win()
                frame.Show()
                self.Close()

    def odustani(self, event):
        self.Close()


# app

if __name__ == "__main__":
    app = wx.App()
    login().Show()
    app.MainLoop()
