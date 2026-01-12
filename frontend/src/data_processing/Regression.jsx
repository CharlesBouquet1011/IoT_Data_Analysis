// Copyright 2025 Paul-Henri Lucotte

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

export function Regression() {
  const { catList, mois, annee } = useChoosedData()

  const [result, setResult] = useState(null)
  const [erreur, setErreur] = useState("")
  const [loading, setLoading] = useState(false)

  async function runRegression(dataType) {
    setErreur("")
    setResult(null)
    setLoading(true)

    const payload = {
      year: annee,
      month: mois,
      data_type: dataType
    }

    try {
      const response = await fetch("http://localhost:8000/api/regression", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || "Erreur serveur")
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setErreur(err.message)
    } finally {
      setLoading(false)
    }
  }

  const stats = result?.stats
  const images = result?.images

  return (
    <div className="space-y-8">

      {/* Error */}
      {erreur && (
        <p className="text-red-600 bg-red-50 p-3 rounded border">
          {erreur}
        </p>
      )}

      {/* Buttons */}
      <div className="space-x-2">
        {catList.map((cat) => (
          <button
            key={cat}
            onClick={() => runRegression(cat)}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            {loading ? "Calcul..." : `Régression : ${cat}`}
          </button>
        ))}
      </div>

      {/* RESULTS */}
      {result && (
        <div className="space-y-10">
          {/* GENERAL STATS */}
          {stats?.general && (
            <div className="border rounded bg-gray-50 p-4">
              <h2 className="text-xl font-semibold text-black mb-4">Statistiques générales</h2>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-black">
                {Object.entries(stats.general).map(([key, value]) => (
                  <li key={key} className="flex justify-between">
                    <span className="font-medium">{key}</span>
                    <span>{String(value)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {/* RSSI */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-black">RSSI</h2>

            {images?.rssi && (
              <img
                src={images.rssi}
                alt="RSSI plot"
                className="max-w-full rounded border"
              />
            )}

            {stats?.rssi && (
              <div className="border rounded bg-gray-50 p-4">
                <h3 className="font-semibold text-black mb-2">Statistiques RSSI</h3>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-black">
                  {Object.entries(stats.rssi).map(([key, value]) => (
                    <li key={key} className="flex justify-between">
                      <span className="font-medium">{key}</span>
                      <span>{typeof value === "number" ? value.toFixed(3) : String(value)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          {/* SNR */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-black">SNR</h2>

            {images?.snr && (
              <img
                src={images.snr}
                alt="SNR plot"
                className="max-w-full rounded border"
              />
            )}

            {stats?.snr && (
              <div className="border rounded bg-gray-50 p-4">
                <h3 className="font-semibold text-black mb-2">Statistiques SNR</h3>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-black">
                  {Object.entries(stats.snr).map(([key, value]) => (
                    <li key={key} className="flex justify-between">
                      <span className="font-medium">{key}</span>
                      <span>{typeof value === "number" ? value.toFixed(3) : String(value)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          {/* RESIDUALS */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-black">Residuals</h2>

            {images?.residuals && (
              <img
                src={images.residuals}
                alt="Residual plots"
                className="max-w-full rounded border"
              />
            )}
          </div>

        </div>
      )}
    </div>
  )
}