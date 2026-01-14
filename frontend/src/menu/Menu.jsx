import { useState, createContext, useContext } from 'react'
import { UploadForm } from '../preprocessing/DropFile'
import DatePicker from 'react-datepicker'
import { AnalysisMenu } from '../preprocessing/AnalysisMenu'
import { Statistiques } from '../data_processing/Stat'
import { Clustering } from '../data_processing/Clustering'
import { Regression } from '../data_processing/Regression'
import { Trends } from '../data_processing/Trends'
import { DevicePredictionDevEUI } from '../prediction/DevicePredictionDevEUI'
import { DevicePredictionDevAdd } from '../prediction/DevicePredictionDevAdd'

import 'react-datepicker/dist/react-datepicker.css'

const DataContext = createContext();

export function MenuPrincipal(){
    const [selection,setSelection]=useState(0)

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="bg-white rounded-xl shadow-md p-6">
                <header className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-gray-800">Outils de traitement</h2>
                    <p className="text-sm text-gray-500">Choisissez une action</p>
                </header>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <button
                        onClick={() => setSelection(1)}
                        className={`flex items-center space-x-3 p-4 rounded-lg border ${selection===1? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 bg-white'} shadow-sm hover:shadow-md transition`}
                        aria-pressed={selection===1}
                    >
                        <div className="text-left">
                            <div className="text-gray-900 font-medium font-semibold">📤 Upload</div>
                            <div className="text-sm text-gray-500">Importez des données pour prétraitement</div>
                        </div>
                    </button>

                    <button
                        onClick={() => setSelection(2)}
                        className={`flex items-center space-x-3 p-4 rounded-lg border ${selection===2? 'border-green-400 bg-green-50' : 'border-gray-200 bg-white'} shadow-sm hover:shadow-md transition`}
                        aria-pressed={selection===2}
                    >
                        <div className="text-left">
                            <div className="text-gray-900 font-medium font-semibold">📊 Traitement</div>
                            <div className="text-sm text-gray-500">Choisissez parmi plusieurs méthodes d'analyse</div>
                        </div>
                    </button>

                    <button
                        onClick={() => setSelection(3)}
                        className={`flex items-center space-x-3 p-4 rounded-lg border ${selection===3? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 bg-white'} shadow-sm hover:shadow-md transition`}
                        aria-pressed={selection===3}
                    >
                        <div className="text-left">
                            <div className="text-gray-900 font-medium font-semibold">🤖 Prédiction</div>
                            <div className="text-sm text-gray-500">Prédisez la source d'un paquet LoraWAN</div>
                        </div>
                    </button>
                </div>

                <div className="mt-6">
                    {selection === 1 && (<UploadForm />)}
                    {selection === 2 && (<ChooseData />)}
                    {selection === 3 && (<PredictionMenu />)}
                </div>
            </div>
        </div>
    )
}

export function PredictionMenu(){
    const [predictionType, setPredictionType] = useState(0)

    return (
        <div className="bg-white rounded-lg p-5 shadow-inner">
            <h3 className="text-lg font-bold text-gray-800 mb-3">Choisissez le type de prédiction</h3>
            <p className="text-sm text-gray-500 mb-4 font-semibold">Sélectionnez ce que vous souhaitez prédire à partir des caractéristiques radio</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <button
                    onClick={() => setPredictionType(1)}
                    className={`flex flex-col items-start p-4 rounded-lg border ${predictionType===1? 'border-purple-400 bg-purple-50' : 'border-gray-200 bg-white'} shadow-sm hover:shadow-md transition`}
                    aria-pressed={predictionType===1}
                >
                    <div className="text-gray-900 font-medium font-semibold mb-2">🔑 Prédire Dev_EUI</div>
                    <div className="text-sm text-gray-500">Identifiez le dispositif IoT (Dev_EUI) à partir des caractéristiques radio des paquets Join Request</div>
                </button>

                <button
                    onClick={() => setPredictionType(2)}
                    className={`flex flex-col items-start p-4 rounded-lg border ${predictionType===2? 'border-cyan-400 bg-cyan-50' : 'border-gray-200 bg-white'} shadow-sm hover:shadow-md transition`}
                    aria-pressed={predictionType===2}
                >
                    <div className="text-gray-900 font-medium font-semibold mb-2">📍 Prédire Dev_Add</div>
                    <div className="text-sm text-gray-500">Identifiez l'adresse du dispositif (Dev_Add) à partir des caractéristiques radio de tous types de paquets</div>
                </button>
            </div>

            <div className="border-t pt-4">
                {predictionType === 1 && <DevicePredictionDevEUI />}
                {predictionType === 2 && <DevicePredictionDevAdd />}
            </div>
        </div>
    )
}

export function ChooseData(){
    const categories = [
        'Confirmed Data Up','Confirmed Data Down','Join Accept','Join Request',
        'Proprietary','RFU','Stat','Unconfirmed Data Up','Unconfirmed Data Down'
    ]
    const [catList,setCatList]=useState([])
    const [month,setMonth]=useState(null)
    const [year,setYear]=useState(null)
    const [traitement,setTraitement]=useState(0)

    const mois = month ? month.getMonth() + 1 : null
    const annee = year ? year.getFullYear() : null

    return (
        <div className="bg-white rounded-lg p-5 shadow-inner">
            <h3 className="text-lg font-bold text-gray-800 mb-3">Filtrage des données à traiter</h3>
            <p className="text-sm text-gray-500 mb-4 font-semibold">Indiquez la période de recherche ainsi que le type de données à analyser</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <DatePicker selected={year}
                    onChange={(date)=>setYear(date)}
                    showYearPicker
                    dateFormat="yyyy"
                    placeholderText='Choisir une année'
                    className="w-full h-12 px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />

                <DatePicker selected={month}
                    onChange={(date)=>setMonth(date)}
                    showMonthYearPicker
                    dateFormat="MM"
                    placeholderText='Choisir un mois'
                    className="w-full h-12 px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                {categories.map((cat) => (
                    <label key={cat} className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                        <input
                            type='checkbox'
                            checked={catList.includes(cat)}
                            className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
                            onChange={() => setCatList(prev => prev.includes(cat) ? prev.filter(v => v !== cat) : [...prev, cat])}
                        />
                        <span className="text-sm text-gray-800">{cat}</span>
                    </label>
                ))}
            </div>

            {catList.length > 0 && (
                <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                        {catList.map(c => (
                            <span key={c} className="px-3 py-1 text-sm bg-indigo-50 text-indigo-700 rounded-full">{c}</span>
                        ))}
                    </div>
                </div>
            )}

            {(catList.length>0 || month || year) && (
                <DataContext.Provider value={{catList,mois,annee}}>
                    <div className="border-t pt-4">
                        <AnalysisMenu onChoice={(choice) => setTraitement(choice)} />

                        <div className="mt-4">
                            {traitement===1 && <Regression />}
                            {traitement===2 && <Trends />}
                            {traitement===3 && <Clustering />}
                            {traitement===4 && <Statistiques />}
                        </div>
                    </div>
                </DataContext.Provider>
            )}
        </div>
    )
}

export function useChoosedData(){
    const context = useContext(DataContext)
    if (!context){
        throw new Error('useChoosedData doit être utilisé à l\'intérieur du DataContext Provider');
    }
    return context
}