# -*- coding: cp1252 -*-
import Tkinter as tk
import threading
import tkFileDialog
import tkMessageBox
import ttk
import subprocess
import os

#-----------------------------------------------------------------------------------------
#--------- Constroi a GUI  --------------------------------------
#------------------------------------------------------------------------------------------
class Janela(threading.Thread):
	def __init__(self, group=None, target=None, name=None,
				args=(), kwargs=None, verbose=None):
		''' Deriva a classe threading, permitindo a passagem
		de argumentos na inicializacao da classe '''
		threading.Thread.__init__(self, group=group, target=target,
							name=name, verbose=verbose)
		
		#os argumentos passados sao armaz. em variaveis internas
		#args eh uma tupla e kwargs eh um dicionario
		self.args = args
		self.kwargs = kwargs
		
		#------------- variaveis internas ---------------
		
		self.spice = self.args[0] #objeto que controla o NGSpice rodando em segundo plano
		#------------------------------------------------------------
		
		self.start()
	
	def sai(self):
		self.raiz.quit()

	def run(self):
		''' Modifica o metodo run da classe threading'''
		
		# constroi a GUI tk normalmente
		self.raiz = tk.Tk()
		self.raiz.protocol("WM_DELETE_WINDOW", self.sai)
		
		#------------------------------------------
		#Cria os botões
		
		self.b_abre_circ = tk.Button(self.raiz, text='Circuito',
							command=self.ng_abre_circ)
		self.b_abre_circ.grid(row=1, column=0)
		
		
		
		
		
		
		#------ botoes de execucao ----------
		
		self.f_exec = ttk.Frame(self.raiz)
		self.f_exec.grid(row=1, column=1)
		self.b_exec = tk.Button(self.f_exec, text='Executa',
							command=self.ng_exec)
		self.b_exec.grid(row=0, column=0)
		
		self.b_para = tk.Button(self.f_exec, text='Parada',
							command=self.ng_para)
		self.b_para.grid(row=1, column=0)
		
		self.b_retoma = tk.Button(self.f_exec, text='Retoma',
							command=self.ng_retoma)
		self.b_retoma.grid(row=2, column=0)
		
		self.b_run = tk.Button(self.f_exec, bg = 'Green')
		self.b_run.grid(row=0, column=1)
		
		#------------------------------------------
		#Cria a area de texto de log
		self.f_log = ttk.Frame(self.raiz)
		self.f_log.grid(row=7, column=0, columnspan=6, rowspan=2)
		self.t_log_s = tk.Scrollbar(self.f_log)
		self.t_log_s.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
		self.t_log = tk.Text(self.f_log, height=10, width=70)
		self.t_log.grid(row=0, column=0,)
		self.t_log_s.config(command=self.t_log.yview)
		self.t_log.config(yscrollcommand=self.t_log_s.set)
		self.t_log.after(100, self.temporal) #atualiza a cada 100 ms
		
		
		#------------------------------------------
		# entradas de texto
		tk.Label(self.raiz, text='Comando:').grid(row=0, column=0, sticky=tk.E)
		self.e_comando = tk.Entry(self.raiz, width=50)
		self.e_comando.grid(row=0, column=1, columnspan=2, sticky=tk.W)
		self.e_comando.delete(0, tk.END)
		self.e_comando.bind('<Return>', self.ng_comando)
		
		#---------------- monitoramento real time
		self.f_monit = tk.Frame(self.raiz, bd=2, relief=tk.RAISED)
		self.f_monit.grid(row=1, column=2)
		
		tk.Label(self.f_monit, text='Monitoramento Real-time:').grid(row=0, column=0, sticky=tk.W)
		
		tk.Label(self.f_monit, text='Variavel:').grid(row=1, column=0, sticky=tk.W)
		self.e_var = tk.Entry(self.f_monit)
		self.e_var.grid(row=2, column=0, sticky=tk.W)
		
		tk.Label(self.f_monit, text='Valor:').grid(row=1, column=1, sticky=tk.W)
		self.e_monit = tk.Entry(self.f_monit)
		self.e_monit.grid(row=2, column=1, sticky=tk.W)
		self.e_monit.delete(0, tk.END)
		
		#------------plots disponiveis
		self.f_plots = ttk.Frame(self.raiz)
		self.f_plots.grid(row=3, column=0)
		self.b_plots = tk.Button(self.f_plots, text='Lista Plots',
							command=self.ng_plots)
		self.b_plots.grid(row=0, column=0)
		
		self.cb_plots = ttk.Combobox(self.f_plots)
		self.cb_plots.grid(row=1, column=0)
		
		#-------------------------------------------
		# Ferramentas de plotagem
		self.f_plot = ttk.Frame(self.raiz)
		self.f_plot.grid(row=3, column=1, columnspan=3, rowspan=2)
		
		self.b_vetores = tk.Button(self.f_plot, text='Lista Vetores',
							command=self.ng_vetores)
		self.b_vetores.grid(row=0, column=0)
		
		self.b_ver_vetor = tk.Button(self.f_plot, text='Imprime Vetor',
							command=self.ng_vetor)
		self.b_ver_vetor.grid(row=2, column=2)
		
		self.b_add_vetor = tk.Button(self.f_plot, text='->',
							command=self.add_vet)
		self.b_add_vetor.grid(row=1, column=2)
		
		self.b_sub_vetor = tk.Button(self.f_plot, text='<-',
							command=self.sub_vet)
		self.b_sub_vetor.grid(row=3, column=2)
		
		self.b_plota = tk.Button(self.f_plot, text='Plota Vetores',
							command=self.plotar)
		self.b_plota.grid(row=0, column=3)
		
		self.l_vetores = tk.Listbox(self.f_plot, selectmode='multiple')
		self.l_vetores.grid(row=1, column=0, rowspan=3, sticky=tk.E+tk.N+tk.S)
		self.l_vetores_s = tk.Scrollbar(self.f_plot)
		self.l_vetores_s.grid(row=1, column=1,rowspan=3, sticky=tk.W+tk.N+tk.S)
		self.l_vetores_s.config(command=self.l_vetores.yview)
		self.l_vetores.config(yscrollcommand=self.l_vetores_s.set)
		
		self.l_plot = tk.Listbox(self.f_plot, selectmode='multiple')
		self.l_plot.grid(row=1, column=3, rowspan=3, sticky=tk.E+tk.N+tk.S)
		self.l_plot_s = tk.Scrollbar(self.f_plot)
		self.l_plot_s.grid(row=1, column=4,rowspan=3, sticky=tk.W+tk.N+tk.S)
		self.l_plot_s.config(command=self.l_plot.yview)
		self.l_plot.config(yscrollcommand=self.l_plot_s.set)
		
		self.raiz.mainloop()	#entra no mainloop da Tk
	
	def ng_ver_dir(self):
		self.spice.cmd('cd')

	def ng_exec(self):
		self.spice.cmd('bg_run')
		
	def ng_para(self):
		self.spice.cmd('bg_halt')
		
	def ng_retoma(self):
		self.spice.cmd('bg_resume')
		
	def ng_vetores(self):
		self.l_vetores.delete(0,tk.END)
		nomes = self.spice.vectorNames(self.cb_plots.get())
		for i in nomes:
			self.l_vetores.insert(tk.END, i)
		
	def ng_vetor(self):
		lista_i = self.l_vetores.curselection()
		for ind in lista_i:
			nome = self.l_vetores.get(ind)
			vet = self.spice.vector(nome)
			self.t_log.config(state=tk.NORMAL) #permite a escrita
			for i in vet:
				self.t_log.insert(tk.END, str(i) + '\n') #insere texto
			self.t_log.see(tk.END) #rola automaticamente
			self.t_log.config(state=tk.DISABLED) #somente leitura
		
	def ng_comando(self, event):
		self.spice.cmd(str(self.e_comando.get()))
		self.e_comando.delete(0, tk.END)
		
	def ng_plots(self):
		self.cb_plots['values'] = self.spice.plots()
	
	def add_vet(self):
		lista_i = self.l_vetores.curselection()
		for ind in lista_i:
			nome = self.l_vetores.get(ind)
			self.l_plot.insert(tk.END,nome)
	
	def sub_vet(self):
		lista_i = self.l_plot.curselection()
		for ind in lista_i:
			self.l_plot.delete(ind)
			
	def plotar(self):
		dir = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/'
		arq_data = dir + 'plot'
		arq_gnu = dir + 'gnu_com'
		lista = self.l_plot.get(0, tk.END)
		if len(lista) > 0:
			if self.cb_plots.get() != '':
				self.spice.cmd('setplot ' + self.cb_plots.get())			
			comm_spice = 'wrdata ' + arq_data
			for i in lista:
				comm_spice = comm_spice + ' ' + str(i)
			self.spice.cmd(comm_spice)
			
			p_plot = 'plot '
			for i in range(len(lista)):
				p_plot = p_plot + '"' + arq_data + '.data" using '
				p_plot = p_plot + str(1+i*2) + ':' + str(2+i*2)
				p_plot = p_plot + ' title "' + str(lista[i]) + '" with lines'
				if i < (len(lista)-1):
					p_plot = p_plot + ', \\\n'
			
			with open(arq_gnu, 'w') as file_:
				file_.write(p_plot)

			proc = subprocess.Popen(['E:/documentos/prog/contrade/gnuplot/bin/gnuplot.exe -persist ' + arq_gnu], shell=True,
					stdin=None, stdout=None, stderr=None, close_fds=True)
	# -----------------------------------------
	#Comando de abrir arquivo
	#------------------------------------------
	def ng_abre_circ(self):
		arquivo = tkFileDialog.askopenfilename(title='Abrir')
		if arquivo:
			if os.path.exists(arquivo):
				self.spice.cmd('source ' + str(arquivo))
			#with open(arquivo) as f:
				#for num_linha, line in enumerate(f):
					#pass
	#------------------------------------------
	#rotina temporal
	#--------------------------------------------
	def temporal(self):
		self.t_log.config(state=tk.NORMAL) #permite a escrita
		while not self.spice.log.empty():
			mens = self.spice.log.get()
			self.t_log.insert(tk.END, mens + '\n') #insere texto
			self.t_log.see(tk.END) #rola automaticamente
		self.t_log.config(state=tk.DISABLED) #somente leitura
		
		self.e_monit.delete(0, tk.END)
		
		try:
			vetor = self.spice.vetores[self.e_var.get()]
		except KeyError:
			vetor = None
		
		try:
			teste = vetor.creal
		except AttributeError:
			vetor = None
		
		if vetor:
			self.e_monit.insert(tk.END, str(vetor.creal))
		else:
			self.e_monit.insert(tk.END, '-')
			
		if not self.spice.em_exec:
			self.b_run.configure(bg = 'Red')
		else:
			self.b_run.configure(bg = 'Green')
		
		self.t_log.after(100, self.temporal) # reagenda
		
if __name__ == "__main__":
	print 'Modulo que constroi a GUI Tk/Tcl da biblioteca do NGSpice'