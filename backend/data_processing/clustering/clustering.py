# Vous pouvez utiliser l'outil CLI, pour en apprendre plus sur l'utilisation de ce dernier, exécutez le script avec l'option --help.
# ```python backend/data_processing/clustering/clustering.py --help``` ; depuis la racine

# Ce script permet de générer des graphiques 1D ou 2D à partir des json prétraités (axes basés sur des métriques choisies).
# On peut alors mieux visualiser la répartition des paquets selon certaines métriques (ex: Airtime, BitRate, RSSI, SNR, ...).

# Note : le dossier de save par défaut est ../Images

import os
import json
from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd

# Import de la fonction centralisée de chargement des données
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from preprocessing.useData import Choose_Open

"""
	Charge les données JSON pour le mois/année donnés et trace un graphique de clustering.

	Paramètres:
	- year (int): année (ex: 2023)
	- month (int): mois (1-12) ou chaîne numérique (ex: 10)
	- data_type (str): type de fichier (ex: 'Confirmed Data Up', 'Join Request', 'Proprietary', ...)
	- n_metrics (int): 1, 2 ou 3 (nombre de métriques à utiliser pour le tracé)
	- metrics (List[str]): liste des noms d'attribut(s) à utiliser (ex: ['Airtime'], ['Airtime','BitRate'] ou ['Airtime','BitRate','rssi'])
	- show (bool): si True, appelle `plt.show()`
	- save_path (str|None): chemin pour sauvegarder l'image PNG (si fourni)
	- max_points (int|None): limiter le nombre de paquets tracés (pratique pour très gros fichiers)

	Retourne:
	- (fig, ax): l'objet figure et axes matplotlib créés.
"""

def plot_clustering(year: int,
					month: int,
					data_type: str,
					n_metrics: int,
					metrics: List[str],
					show: bool = True,
					save_path: Optional[str] = None,
					max_points: Optional[int] = None) -> Tuple[plt.Figure, Union[plt.Axes, Axes3D], Optional[str]]:

	month_str = str(int(month))

	try:
		df = Choose_Open(year, month, (data_type,))
		
		# Convertir le DataFrame en liste de dictionnaires pour compatibilité avec le code existant
		# Si l'index est @timestamp, le réinitialiser pour l'inclure comme colonne
		if df.index.name == '@timestamp':
			df_reset = df.reset_index()
		else:
			df_reset = df
		
		entries = df_reset.to_dict(orient='records')
		
	except Exception as e:
		# Si Choose_Open échoue, fallback sur l'ancienne méthode de chargement
		print(f"Avertissement: Impossible d'utiliser Choose_Open ({e}), fallback sur chargement JSON direct")
		
		base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "preprocessing", "Data")
		base_dir = os.path.normpath(base_dir)
		data_dir = os.path.join(base_dir, str(year), month_str)

		if not os.path.isdir(data_dir):
			raise FileNotFoundError(f"Dossier inexistant à {data_dir}")

		known_files = {
			"confirmed data up": "Confirmed Data Up.json",
			"confirmed data down": "Confirmed Data Down.json",
			"join accept": "Join Accept.json",
			"join request": "Join Request.json",
			"proprietary": "Proprietary.json",
			"rfu": "RFU.json",
			"stat": "Stat.json",
			"unconfirmed data up": "Unconfirmed Data Up.json",
			"unconfirmed data down": "Unconfirmed Data Down.json"
		}

		key = data_type.strip().lower()
		filename = known_files.get(key, None)
		if filename is None:
			for k, v in known_files.items():
				if k in key or key in k:
					filename = v
					break

		if filename is None:
			maybe = data_type if data_type.lower().endswith(".json") else data_type + ".json"
			candidate = os.path.join(data_dir, maybe)
			if os.path.isfile(candidate):
				filename = maybe

		# Gestion des erreurs (absence de fichier)
		if filename is None:
			raise FileNotFoundError(f"Fichier pour '{data_type}' introuvable dans {data_dir}")
			
		filepath = os.path.join(data_dir, filename)
		if not os.path.isfile(filepath):
			raise FileNotFoundError(f"Fichier inexistant à {filepath}")

		# Ouverture et import du fichier JSON
		with open(filepath, 'r', encoding='utf-8') as f:
			content = f.read().strip()
			
		# Essayer de parser comme JSON standard
		try:
			data = json.loads(content)
		except json.JSONDecodeError:
			# Si échec, essayer comme JSON Lines (une ligne = un objet JSON)
			entries = []
			for line in content.splitlines():
				line = line.strip()
				if not line:
					continue
				try:
					entries.append(json.loads(line))
				except json.JSONDecodeError:
					continue
		else:
			# Extraction des entrées du fichier
			if isinstance(data, dict):
				entries = list(data.values())
			elif isinstance(data, list):
				entries = data
			else:
				raise ValueError("Format invalide")

    # Validation des paramètres
	if n_metrics not in (1, 2, 3):
		raise ValueError("n_metrics doit être 1, 2 ou 3")

	if not isinstance(metrics, list) or len(metrics) < n_metrics:
		raise ValueError(f"Fournir au moins {n_metrics} métriques valables")

    # Extraction des valeurs des métriques
	vals_x = []
	vals_y = []
	vals_z = []
	count = 0
	for e in entries:
		if max_points and count >= max_points:
			break
		try:
			if n_metrics == 1:
				v = e.get(metrics[0], None)
				if v is None:
					continue
				xv = float(v)
				vals_x.append(xv)
				count += 1
			elif n_metrics == 2:
				v1 = e.get(metrics[0], None)
				v2 = e.get(metrics[1], None)
				if v1 is None or v2 is None:
					continue
				xv = float(v1)
				yv = float(v2)
				vals_x.append(xv)
				vals_y.append(yv)
				count += 1
			else:  # n_metrics == 3
				v1 = e.get(metrics[0], None)
				v2 = e.get(metrics[1], None)
				v3 = e.get(metrics[2], None)
				if v1 is None or v2 is None or v3 is None:
					continue
				xv = float(v1)
				yv = float(v2)
				zv = float(v3)
				vals_x.append(xv)
				vals_y.append(yv)
				vals_z.append(zv)
				count += 1
		except (TypeError, ValueError):
			continue

    # Des métriques inexistantes ou sans données valides sont spécifiées
	if len(vals_x) == 0:
		raise ValueError("Il n'y a pas de données valides pour les métriques spécifiées.")

	# Créer la figure avec projection 3D si nécessaire
	if n_metrics == 3:
		fig = plt.figure(figsize=(10, 8))
		ax = fig.add_subplot(111, projection='3d')
	else:
		fig, ax = plt.subplots(figsize=(8, 5))

	# Tracé adaptatif pour une seule métrique (1D)
	if n_metrics == 1:
		# Agréger les points identiques (même valeur de métrique)
		unique_vals, counts = np.unique(vals_x, return_counts=True)
		y = np.zeros(len(unique_vals))
		val_min, val_max = float(np.min(unique_vals)), float(np.max(unique_vals))
		range_val = val_max - val_min if val_max != val_min else 1.0
		pad = 0.02 * range_val
		ax.set_xlim(val_min - pad, val_max + pad)
		xgrads = ax.get_xticks()
		if len(xgrads) > 1:
			diffs = np.diff(np.sort(xgrads))
			pos = diffs[diffs > 0]
			spacing = float(np.min(pos)) if pos.size > 0 else range_val
		else:
			spacing = range_val

		x0_disp = ax.transData.transform((val_min, 0))[0]
		x1_disp = ax.transData.transform((val_min + spacing, 0))[0]
		pixel_diff = abs(x1_disp - x0_disp)
		# Eviter division par zéro
		if fig.dpi and pixel_diff > 0:
			max_diameter_points = pixel_diff * 72.0 / fig.dpi
		else:
			max_diameter_points = 10.0

		max_diameter_points *= 0.9
		max_area = max_diameter_points ** 2

		raw = counts.astype(float)
		if raw.max() > 0:
			sizes = (raw / raw.max()) * max_area
		else:
			sizes = np.full_like(raw, fill_value=(max_area * 0.2))

		min_diameter_points = 2.0
		min_area = min_diameter_points ** 2
		sizes = np.clip(sizes, min_area, max_area)

		ax.scatter(unique_vals, y, s=sizes, alpha=0.6)
		ax.set_xlabel(metrics[0])
		ax.set_yticks([])
		ax.set_title(f"Distribution de '{metrics[0]}' - {data_type} {month_str}/{year}")
		ax.grid(axis='x', linestyle='--', alpha=0.4)

	# Tracé adaptatif pour une deux métriques (2D)
	elif n_metrics == 2:
		# Agréger les points identiques (même valeur sur les deux métriques)
		pts = np.column_stack((vals_x, vals_y))
		unique_pts, counts = np.unique(pts, axis=0, return_counts=True)
		ux = unique_pts[:, 0]
		yu = unique_pts[:, 1]

		ax.set_xlabel(metrics[0])
		ax.set_ylabel(metrics[1])
		ax.set_title(f"{metrics[0]} vs {metrics[1]} - {data_type} {month_str}/{year}")

		x_min, x_max = float(np.min(ux)), float(np.max(ux))
		y_min, y_max = float(np.min(yu)), float(np.max(yu))
		rx_range = x_max - x_min if x_max != x_min else 1.0
		ry_range = y_max - y_min if y_max != y_min else 1.0
		x_pad = 0.02 * rx_range
		y_pad = 0.02 * ry_range
		ax.set_xlim(x_min - x_pad, x_max + x_pad)
		ax.set_ylim(y_min - y_pad, y_max + y_pad)

		xgrads = ax.get_xticks()
		if len(xgrads) > 1:
			diffs = np.diff(np.sort(xgrads))
			pos = diffs[diffs > 0]
			spacing = float(np.min(pos)) if pos.size > 0 else rx_range
		else:
			spacing = rx_range

		x0_disp = ax.transData.transform((x_min, 0))[0]
		x1_disp = ax.transData.transform((x_min + spacing, 0))[0]
		pixel_diff = abs(x1_disp - x0_disp)
		if fig.dpi and pixel_diff > 0:
			max_diameter_points = pixel_diff * 72.0 / fig.dpi
		else:
			max_diameter_points = 10.0
		max_diameter_points *= 0.9
		max_area = max_diameter_points ** 2

		raw = counts.astype(float)
		if raw.max() > 0:
			sizes = (raw / raw.max()) * max_area
		else:
			sizes = np.full_like(raw, fill_value=(max_area * 0.2))

		min_diameter_points = 2.0
		min_area = min_diameter_points ** 2
		sizes = np.clip(sizes, min_area, max_area)

		ax.scatter(ux, yu, s=sizes, alpha=0.6)
		ax.grid(True, linestyle='--', alpha=0.4)

	# Tracé adaptatif pour trois métriques (3D)
	elif n_metrics == 3:
		# Agréger les points identiques (même valeur sur les trois métriques)
		pts = np.column_stack((vals_x, vals_y, vals_z))
		unique_pts, counts = np.unique(pts, axis=0, return_counts=True)
		ux = unique_pts[:, 0]
		uy = unique_pts[:, 1]
		uz = unique_pts[:, 2]

		ax.set_xlabel(metrics[0])
		ax.set_ylabel(metrics[1])
		ax.set_zlabel(metrics[2])
		ax.set_title(f"{metrics[0]} vs {metrics[1]} vs {metrics[2]} - {data_type} {month_str}/{year}")

		x_min, x_max = float(np.min(ux)), float(np.max(ux))
		y_min, y_max = float(np.min(uy)), float(np.max(uy))
		z_min, z_max = float(np.min(uz)), float(np.max(uz))
		rx_range = x_max - x_min if x_max != x_min else 1.0
		ry_range = y_max - y_min if y_max != y_min else 1.0
		rz_range = z_max - z_min if z_max != z_min else 1.0
		x_pad = 0.02 * rx_range
		y_pad = 0.02 * ry_range
		z_pad = 0.02 * rz_range
		ax.set_xlim(x_min - x_pad, x_max + x_pad)
		ax.set_ylim(y_min - y_pad, y_max + y_pad)
		ax.set_zlim(z_min - z_pad, z_max + z_pad)

		# Calcul des tailles de points basé sur les comptes
		raw = counts.astype(float)
		if raw.max() > 0:
			sizes = (raw / raw.max()) * 100 + 20  # Taille entre 20 et 120
		else:
			sizes = np.full_like(raw, fill_value=50, dtype=float)

		# Tracer les points 3D
		ax.scatter(ux, uy, uz, s=sizes, alpha=0.6, c=uz, cmap='viridis')
		ax.grid(True, linestyle='--', alpha=0.4)

	fig.tight_layout()

	# Default images folder: ../../Images
	images_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Images'))

    # Nettoie le nom du fichier pour qu'il soit valide
	def _sanitize(s: str) -> str:
		keep = []
		for ch in s:
			if ch.isalnum() or ch in ('-', '_'):
				keep.append(ch)
			elif ch.isspace():
				keep.append('_')
		return ''.join(keep)

    # Génère le nom de fichier par défaut
	def _make_default_filename() -> str:
		dt = _sanitize(data_type.replace(' ', '_'))
		mets = '_'.join([_sanitize(m) for m in metrics[:n_metrics]])
		return f"{dt}_{year:04d}-{int(month):02d}_{mets}.png"

    # Gestion du chemin de sauvegarde
	if save_path:
		if os.path.dirname(save_path) == '':
			os.makedirs(images_dir, exist_ok=True)
			save_path_final = os.path.join(images_dir, save_path)
		else:
			os.makedirs(os.path.dirname(save_path), exist_ok=True)
			save_path_final = save_path
	else:
		os.makedirs(images_dir, exist_ok=True)
		save_path_final = os.path.join(images_dir, _make_default_filename())

	if save_path_final:
		fig.savefig(save_path_final, dpi=150)

	if show:
		plt.show()

	return fig, ax, save_path_final

# Définit l'usage CLI de l'outil
# Documentation accessible via --help

__all__ = ['clustering']

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(
		description='Trace un graphique 1D ou 2D à partir des données JSON prétraitées'
	)
	# Arguments obligatoires positionnels (à spécifier obligatoirement dans cet ordre : <year> <month> <data_type>)
	parser.add_argument('year', type=int, help='Année des données (ex: 2023)')
	parser.add_argument('month', type=int, help='Mois des données (1-12)')
	parser.add_argument('data_type', type=str, help='Type de données (ex: "Confirmed Data Up")')
	# Arguments optionnels (doivent être spécifiés avec leur préfixe)
	parser.add_argument('--metrics', '-m', nargs='+', required=True, help='Métrique(s) à utiliser (ex: Airtime BitRate rssi)')
	parser.add_argument('--n-metrics', '-n', type=int, choices=[1, 2, 3], help='Nombre de métriques (1, 2 ou 3). Si non spécifié, automatiquement déduit de -m')
	parser.add_argument('--save', '-s', type=str, default=None, help='Chemin pour sauvegarder le graphique image')
	parser.add_argument('--max-points', type=int, default=None, help='Limiter le nombre de paquets tracés')
	parser.add_argument('--no-show', action='store_true', help="Ne pas appeler plt.show(), uniquement l'export")

	args = parser.parse_args()

	n_metrics = args.n_metrics or len(args.metrics)

	try:
		fig, ax, saved = plot_clustering(
			year=args.year,
			month=args.month,
			data_type=args.data_type,
			n_metrics=n_metrics,
			metrics=args.metrics,
			show=(not args.no_show),
			save_path=args.save,
			max_points=args.max_points,
		)
	except Exception as e:
		print(f"Erreur: {e}")
		raise
	else:
		if saved:
			print(f"Graphique sauvegardé à {saved}")
		if not args.no_show:
			print("Affichage du graphique terminé.")