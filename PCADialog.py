from tkinter import *
import numpy as np

# Dialog box built to display the results of PCA Analysis in the program
class PCADialog:
# potential extension for later: allow user to change rounding cutoff
	def __init__(self, parent, pca_obj):
		top = self.top = Toplevel(parent)
		Label(top, text="PCA Results").pack(pady=6)
		main = self.mainframe = Frame(top)
		main.pack(side=TOP, padx=4, pady=4, fill=Y)
		# Display PCA Results
		eigenvecs = pca_obj.get_eigenvectors().tolist()
		eigenvals = pca_obj.get_eigenvalues().tolist()
		final_total = np.sum(eigenvals)
		eigen_total = 0
		for rowv in range(len(eigenvecs)):
			# Sum the total of eigenvalues so far
			eigen_total += eigenvals[rowv]
			# Label each row with assigned eigenvector names
			entry = Label(main, text=pca_obj.headers[rowv])
			entry.grid(row=(rowv + 1), column=0, sticky=(W,E), ipadx=4)
			for colv in range(len(eigenvecs[rowv])):
				# Label each column with appropriate headers
				entry = Label(main, text=pca_obj.get_original_headers()[colv])
				entry.grid(row=0, column=(colv + 3), sticky=(W,E), ipadx=4)
				if colv == 0:
					# Label first three columns appropriately
					entry = Label(main, text="E-vec")
					entry.grid(row=0, column=(colv), sticky=(W,E), ipadx=4)
					entry = Label(main, text="E-val")
					entry.grid(row=0, column=(colv + 1), sticky=(W,E), ipadx=4)
					entry = Label(main, text="Cumulative")
					entry.grid(row=0, column=(colv + 2), sticky=(W,E), ipadx=4)
				elif colv == 1:
					# Insert eigenvalues into grid
					entry = Label(main, text=str(np.round(eigenvals[rowv], 3)))
					entry.grid(row=(rowv + 1), column=(colv), sticky=(W,E), ipadx=4)
				elif colv == 2:
					# Divide total of eigenvalues so far by final total to get cumulative
					entry = Label(main, text=str(np.round((eigen_total / final_total), 3)))
					entry.grid(row=(rowv + 1), column=(colv), sticky=(W,E), ipadx=4)
				# Insert values for each column in projected data
				entry = Label(main, text=str(np.round(eigenvecs[rowv][colv], 3)))
				entry.grid(row=(rowv + 1), column=(colv + 3), sticky=(W,E), ipadx=4)
				# print("row: ", rowv, "  col: ", colv)
		# End Display PCA Results
		b = Button(top, text="OK", command=self.ok)
		b.pack(pady=3, padx=10)

	def ok(self):
		# print("value is", self.e.get())
		self.top.destroy()

# root = Tk()
# Button(root, text="Hello!").pack()
# root.update()
# d = MyDialog(root)
# root.wait_window(d.top)