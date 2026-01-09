// Copyright 2025 Titouan Verdier

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { useState } from "react"
import { useChoosedData } from "../menu/Menu"

export function Clustering() {
  const { catList, mois, annee } = useChoosedData()
  console.log("useChoosedData:", { catList, mois, annee })
  const [selectedMetrics, setSelectedMetrics] = useState([])
  const [nMetrics, setNMetrics] = useState(1)
  const [images, setImages] = useState({})
  const [erreur, setErreur] = useState("")
  const [loading, setLoading] = useState(false)

  // Liste des métriques disponibles pour le clustering, celles qui sont des valeurs numériques
  const availableMetrics = [
    "Airtime",
    "BitRate",
    "rssi",
    "lsnr",
    "size",
    "freq",
    "SF",
    "Bandwidth"
  ]

  async function processClustering() {
    setErreur("")
    setLoading(true)
    
    // if (selectedMetrics.length === 0) {
    //   setErreur("Veuillez sélectionner au moins une métrique")
    //   setLoading(false)
    //   return
    // }

    // if (selectedMetrics.length < nMetrics) {
    //   setErreur(`Veuillez sélectionner au moins ${nMetrics} métrique(s)`)
    //   setLoading(false)
    //   return
    // }

    // if (!catList || catList.length === 0) {
    //   setErreur("Veuillez sélectionner au moins un type de données")
    //   setLoading(false)
    //   return
    // }
    // if (!selectedYear || !selectedMonth) {
    //   setErreur("Veuillez sélectionner une année et un mois dans le menu principal")
    //   setLoading(false)
    //   return
    // }

    const requestData = {
      year: annee,
      month: mois,
      data_types: catList,
      n_metrics: nMetrics,
      metrics: selectedMetrics.slice(0, nMetrics)
    }

    console.log("Données envoyées:", requestData)

    try {
      const response = await fetch("http://localhost:8000/api/clustering", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
      })

      console.log("Response status:", response.status)
      console.log("Response ok:", response.ok)

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        console.log("Erreur response:", errData)
        setErreur(errData.detail || errData.error || `Erreur ${response.status}`)
        setImages({})
      } else {
        console.log("Clustering réussi")
        setErreur("")
        const data = await response.json()
        setImages(data.images || {})
      }
    } catch (error) {
      console.error("Erreur lors du clustering:", error)
      setErreur("Erreur de communication avec le serveur")
      setImages({})
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Sélection du nombre de métriques */}
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="text-lg font-semibold text-gray-800 mb-3">
          Nombre de métriques pour le tracé
        </h4>
        <p className="text-sm text-gray-600 mb-3">
          Choisissez la représentation souhaitée
        </p>
        <div className="flex gap-4 justify-center">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="nMetrics"
              value={1}
              checked={nMetrics === 1}
              onChange={() => setNMetrics(1)}
              className="form-radio text-blue-600"
            />
            <span className="text-gray-800">1D</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="nMetrics"
              value={2}
              checked={nMetrics === 2}
              onChange={() => setNMetrics(2)}
              className="form-radio text-blue-600"
            />
            <span className="text-gray-800">2D</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="nMetrics"
              value={3}
              checked={nMetrics === 3}
              onChange={() => setNMetrics(3)}
              className="form-radio text-blue-600"
            />
            <span className="text-gray-800">3D</span>
          </label>
        </div>
      </div>

      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="text-lg font-semibold text-gray-800 mb-3">
          Sélectionnez {nMetrics === 1 ? "la métrique" : nMetrics === 2 ? "les 2 métriques" : "les 3 métriques"} à visualiser
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {availableMetrics.map((metric) => (
            <label
              key={metric}
              className="flex items-center gap-2 text-gray-800 bg-white p-2 rounded shadow-sm hover:bg-gray-100 transition"
            >
              <input
                type="checkbox"
                checked={selectedMetrics.includes(metric)}
                className="h-4 w-4 text-blue-600 border-gray-400 rounded focus:ring-blue-500"
                onChange={() => {
                  setSelectedMetrics((prev) =>
                    prev.includes(metric)
                      ? prev.filter((v) => v !== metric)
                      : [...prev, metric]
                  )
                }}
              />
              <span className="truncate">{metric}</span>
            </label>
          ))}
        </div>
        {selectedMetrics.length > 0 && (
          <div className="mt-3 space-y-1">
            <p className="text-sm text-gray-600">
              Sélectionnées ({selectedMetrics.length}/{nMetrics}) : {selectedMetrics.slice(0, nMetrics).join(", ")}
            </p>
            {selectedMetrics.length > nMetrics && (
              <p className="text-xs text-red-600">
                ⚠️ Veuillez retirer des métriques pour n'en garder que {nMetrics}
              </p>
            )}
            {selectedMetrics.length < nMetrics && (
              <p className="text-xs text-red-600">
                ⚠️ Veuillez sélectionner au moins {nMetrics} métrique(s)
              </p>
            )}
          </div>
        )}
      </div>

      {erreur && (
        <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2">
          {erreur}
        </p>
      )}

      {selectedMetrics.length >= nMetrics && catList.length > 0 && (
        <button
          onClick={processClustering}
          disabled={loading}
          className={`w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
        >
          {loading ? "En cours..." : "Générer"}
        </button>
      )}

      {Object.keys(images).length > 0 && (
        <div className="mt-6 space-y-6">
          {Object.entries(images).map(([dataType, imagePath]) => (
            <div
              key={dataType}
              className="p-4 border border-gray-200 rounded-lg bg-gray-50"
            >
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                {dataType}
              </h3>
              <div className="flex justify-center">
                <a
                  href={imagePath}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <img
                    src={imagePath}
                    alt={`Clustering - ${dataType}`}
                    className="max-w-full h-auto rounded-md border border-gray-300 hover:shadow-lg transition"
                  />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

