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

export function DevicePredictionDevEUI() {
  const [isTraining, setIsTraining] = useState(false)
  const [trainingStatus, setTrainingStatus] = useState("")
  const [trainingOutput, setTrainingOutput] = useState("")
  
  const [formData, setFormData] = useState({
    SF: 7,
    Bandwidth: 125,
    BitRate: 5468.75,
    Coding_rate: "4/5",
    Airtime: 66.816,
    freq: 868.3,
    rssi: -113,
    lsnr: -3.8,
    size: 29,
    Type: "Confirmed Data Up"
  })
  
  const [predictionResult, setPredictionResult] = useState(null)
  const [isPredicting, setIsPredicting] = useState(false)
  const [error, setError] = useState("")

  const typeOptions = [
    "Confirmed Data Up",
    "Confirmed Data Down",
    "Unconfirmed Data Up",
    "Unconfirmed Data Down",
    "Join Request",
    "Join Accept",
    "Proprietary",
    "RFU"
  ]

  const codingRateOptions = ["4/5", "4/6", "4/7", "4/8"]

  async function handleTrain() {
    setIsTraining(true)
    setTrainingStatus("Entraînement en cours...")
    setTrainingOutput("")
    setError("")

    // Connect to SSE endpoint to receive training logs in real-time
    try {
      const es = new EventSource("http://localhost:8000/api/clustering/train/stream")

      es.onmessage = (e) => {
        // special finish token
        if (e.data && e.data.startsWith("__TRAIN_EXIT__")) {
          const parts = e.data.split(" ")
          const code = parts.length > 1 ? Number(parts[1]) : null
          if (code === 0) {
            setTrainingStatus("✅ Modèle entraîné avec succès!")
          } else {
            setTrainingStatus(`Terminé avec code ${code}`)
          }
          es.close()
          setIsTraining(false)
          return
        }

        setTrainingOutput(prev => prev + e.data + "\n")
      }

      es.onerror = (err) => {
        setError("Erreur de connexion au flux d'entraînement")
        es.close()
        setIsTraining(false)
      }

    } catch (err) {
      setError(`Erreur lors de l'entraînement: ${err.message}`)
      setTrainingStatus("")
      setIsTraining(false)
    }
  }

  async function handlePredict(e) {
    e.preventDefault()
    setIsPredicting(true)
    setPredictionResult(null)
    setError("")
    
    try {
      // Convertir les types si nécessaire
      const packet = {
        SF: parseFloat(formData.SF),
        Bandwidth: parseFloat(formData.Bandwidth),
        BitRate: parseFloat(formData.BitRate),
        Coding_rate: formData.Coding_rate,
        Airtime: parseFloat(formData.Airtime),
        freq: parseFloat(formData.freq),
        rssi: parseFloat(formData.rssi),
        lsnr: parseFloat(formData.lsnr),
        size: parseFloat(formData.size),
        Type: formData.Type
      }

      const response = await fetch("http://localhost:8000/api/clustering/predict", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(packet)
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Erreur ${response.status}`)
      }

      const data = await response.json()
      setPredictionResult(data.result)
    } catch (err) {
      setError(`Erreur lors de la prédiction: ${err.message}`)
    } finally {
      setIsPredicting(false)
    }
  }

  function handleInputChange(field, value) {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="p-6 max-w-6xl mx-auto text-gray-800">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        Prédiction de Device IoT
      </h1>

      {/* Section d'entraînement */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          1. Entraînement du modèle
        </h2>
        <p className="text-gray-600 mb-4">
          Commencez par entraîner le modèle avec les données disponibles dans le dossier Data.
        </p>
        
        <button
          onClick={handleTrain}
          disabled={isTraining}
          className={`px-6 py-3 rounded-lg font-medium transition-colors ${
            isTraining
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
        >
          {isTraining ? "Entraînement en cours..." : "Entraîner le modèle"}
        </button>

        {trainingOutput && (
          <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h3 className="font-semibold mb-2">Sortie de l'entraînement:</h3>
            <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto">
              {trainingOutput}
            </pre>
          </div>
        )}
      </div>

      {/* Section de prédiction */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          2. Prédiction de device
        </h2>
        <p className="text-gray-600 mb-6">
          Entrez les caractéristiques d'un paquet pour prédire le device associé.
        </p>

        <form onSubmit={handlePredict} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* SF */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SF (Spreading Factor)
              </label>
              <input
                type="number"
                step="1"
                value={formData.SF}
                onChange={(e) => handleInputChange("SF", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* Bandwidth */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bandwidth (kHz)
              </label>
              <input
                type="number"
                step="any"
                value={formData.Bandwidth}
                onChange={(e) => handleInputChange("Bandwidth", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* BitRate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                BitRate (bps)
              </label>
              <input
                type="number"
                step="any"
                value={formData.BitRate}
                onChange={(e) => handleInputChange("BitRate", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* Coding_rate */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Coding Rate
              </label>
              <select
                value={formData.Coding_rate}
                onChange={(e) => handleInputChange("Coding_rate", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                {codingRateOptions.map(rate => (
                  <option key={rate} value={rate}>{rate}</option>
                ))}
              </select>
            </div>

            {/* Airtime */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Airtime (ms)
              </label>
              <input
                type="number"
                step="any"
                value={formData.Airtime}
                onChange={(e) => handleInputChange("Airtime", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* freq */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fréquence (MHz)
              </label>
              <input
                type="number"
                step="any"
                value={formData.freq}
                onChange={(e) => handleInputChange("freq", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* rssi */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                RSSI (dBm)
              </label>
              <input
                type="number"
                step="any"
                value={formData.rssi}
                onChange={(e) => handleInputChange("rssi", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* lsnr */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                LSNR (dB)
              </label>
              <input
                type="number"
                step="any"
                value={formData.lsnr}
                onChange={(e) => handleInputChange("lsnr", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Size (bytes)
              </label>
              <input
                type="number"
                step="any"
                value={formData.size}
                onChange={(e) => handleInputChange("size", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* Type */}
            <div className="md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type de paquet
              </label>
              <select
                value={formData.Type}
                onChange={(e) => handleInputChange("Type", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                {typeOptions.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={isPredicting}
            className={`w-full px-6 py-3 rounded-lg font-medium transition-colors ${
              isPredicting
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-green-600 hover:bg-green-700 text-white"
            }`}
          >
            {isPredicting ? "Prédiction en cours..." : "Prédire le device"}
          </button>
        </form>

        {/* Affichage des erreurs */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Affichage des résultats */}
        {predictionResult && (
          <div className="mt-6 p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-blue-900">
              Résultat de la prédiction
            </h3>
            
            {predictionResult.prediction && (
              <div className="mb-4">
                <div className="text-2xl font-bold text-blue-800 mb-2">
                  Device prédit: {predictionResult.prediction}
                </div>
                {predictionResult.confidence !== undefined && (
                  <div className="text-lg text-blue-700">
                    Confiance: {(predictionResult.confidence * 100).toFixed(2)}%
                  </div>
                )}
              </div>
            )}

            {predictionResult.candidates && predictionResult.candidates.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-blue-900">
                  Top candidats:
                </h4>
                <div className="space-y-2">
                  {predictionResult.candidates.slice(0, 5).map((candidate, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center bg-white p-3 rounded-lg"
                    >
                      <span className="font-medium text-gray-800">
                        {candidate.device}
                      </span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2.5">
                          <div
                            className="bg-blue-600 h-2.5 rounded-full"
                            style={{ width: `${candidate.proportion * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600 w-16 text-right">
                          {(candidate.proportion * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sortie brute JSON du script predict_device.py */}
            <div className="mt-4">
              <h4 className="font-semibold mb-2 text-blue-900">Sortie brute:</h4>
              <pre className="bg-white text-sm text-gray-800 p-3 rounded-lg overflow-x-auto whitespace-pre-wrap">
{JSON.stringify(predictionResult, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}