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

import React, { useState } from 'react'

export function AnalysisMenu({ onChoice }){
    // Option codes: 1 = regression, 2 = seasonality, 3 = clustering, 4 = trends
    const [selection, setSelection] = useState(null)

    function choose(val){
        const code = Number(val)
        setSelection(code)
        if (typeof onChoice === 'function') onChoice(code)
    }

    return (
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow-md space-y-6">
        <h4 className="text-lg font-semibold text-gray-800">Choisissez la méthode d'analyse souhaitée</h4>
        <div className="grid grid-cols-1 gap-4">
            <label className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between">
            <div>
                <div className="font-medium text-gray-800">Régression / Prédiction</div>
                <div className="text-sm text-gray-500">ajouter une description</div>
            </div>
            <input type="radio" name="analysis" value={1} checked={selection===1} onChange={()=>choose(1)} />
            </label>

            <label className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between">
            <div>
                <div className="font-medium text-gray-800">Analyse de la saisonnalité</div>
                <div className="text-sm text-gray-500">ajouter une description</div>
            </div>
            <input type="radio" name="analysis" value={2} checked={selection===2} onChange={()=>choose(2)} />
            </label>

            <label className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between">
            <div>
                <div className="font-medium text-gray-800">Clustering</div>
                <div className="text-sm text-gray-500">ajouter une description</div>
            </div>
            <input type="radio" name="analysis" value={3} checked={selection===3} onChange={()=>choose(3)} />
            </label>
            <label className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between">
            <div>
                <div className="font-medium text-gray-800">Statistiques</div>
                <div className="text-sm text-gray-500">Statistiques diverses (répartitions de l'utilisation de différents paramètres)</div>
            </div>
            <input type="radio" name="analysis" value={4} checked={selection===5} onChange={()=>choose(4)} />
            </label>
            <label className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between">
            <div>
                <div className="font-medium text-gray-800">MODÈLE DE CHOIX POUR LE MENU</div>
                <div className="text-sm text-gray-500">ajouter une description</div>
            </div>
            <input type="radio" name="analysis" value={5} checked={selection===6} onChange={()=>choose(6)} />
            </label>
        </div>

        {/* <div className="flex justify-end">
            <button
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
            onClick={()=>{
                if (selection) {
                if (typeof onChoice === 'function') onChoice(selection)
                }
            }}
            >
            Lancer
            </button>
        </div> */}
        </div>
    )
}

export default AnalysisMenu
