// Copyright 2025 Charles Bouquet

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
import { useState,useEffect } from "react"
import { useChoosedData } from "../menu/Menu"


export function Statistiques(){
    const {mois,annee} =useChoosedData()
    const [choosedColumns,setChoosedColumns]=useState([]) //on passera sur l'erreur de conjugaison, le code fonctionne
    const [images,setImages]=useState({})
    const [erreur,setErreur]=useState("")
    async function processData(){
        setErreur("")
        if (choosedColumns.length===0){
        setErreur("Veuillez indiquer les colonnes que vous souhaiter traiter")
        return ;
        }
        const response=await fetch("http://localhost:8000/api/stats",{
        method:"POST",
        credentials:"include",
        headers: {
            "Content-Type": "application/json"
        },
        body:JSON.stringify({
            year:annee,
            month:mois,
            columnList:choosedColumns
        })
        })
        console.log("Response status:", response.status)
        console.log("Response ok:", response.ok)
        if (!response.ok){
            const errData = await response.json().catch(() => ({}))
            console.log("Erreur response:", errData)
            setErreur(errData.error || `Erreur ${response.status}`)
            setImages([])
        }
        else{
            console.log("Traitement réussi")
            setErreur("")
            const data= await response.json()
            setImages(data.images)

            
        }
    }

    return(

        <>
        <ChooseColumns choosedColumns={choosedColumns} setChoosedColumns={(columns)=>setChoosedColumns(columns)}></ChooseColumns>
        {erreur && (
            <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2 mt-4">
            {erreur}
            </p>
        )}
        {choosedColumns.length !== 0 && (
            <button
            onClick={() => processData()}
            className="mt-4 w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
            Afficher les résultats
            </button>
        )}
        {Object.keys(images).length>0 &&(
            <DisplayImages images={images} />
        )}
        </>
    )
}



function ChooseColumns({choosedColumns,setChoosedColumns}){
    const columns=["Bandwidth","Coding_rate","GW_EUI","SF","freq","modu","adr","rfch", //métriques pour proportion
        "BitRate","Airtime","lsnr","rssi","size"//métriques pour histogramme

    ]
//     const {mois,annee}=useChoosedData()
//     const [error,setError]=useState(false)
//     const [loaded,setLoaded]=useState(false)
//     useEffect(()=>{
//         async function fetchColumns(){
//             const url = new URL("http://localhost:8000/api/stats/ColumnList");
//             setLoaded(false)
//             if (annee !== undefined && annee !== null) {
//                 url.searchParams.set("annee", annee);
//             }

//             if (mois !== undefined && mois !== null) {
//                 url.searchParams.set("mois", mois);
//             }

//             const response=await fetch(url)
//             if (response.ok){
//                 const data= await response.json()
//                 setLoaded(true)
//                 setColumns(data.liste)
//                 setError(false)
//             }else{
//                 setError(true)
//                 console.error("Erreur Serveur")
//             }
//         }
//         fetchColumns()
        

//     },
// [mois,annee])
    


    return(
        <>
        
        {/* {columns.length===0 && (
            <>
            {loaded?<div className="flex items-center gap-2 text-gray-500 animate-pulse">
                <div className="h-4 w-4 rounded-full border-2 border-gray-400 border-t-transparent animate-spin" />
                <span>Aucune colonne pour la période sélectionnée</span>
            </div>
            :
            
            <div className="flex items-center gap-2 text-gray-500 animate-pulse">
                <div className="h-4 w-4 rounded-full border-2 border-gray-400 border-t-transparent animate-spin" />
                <span>Chargement des colonnes…</span>
            </div>
            }
            
       </> ) } */}
        {columns.length!==0 &&(
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {columns.map((column) => (
                    <label
                    key={column}
                    className="flex items-center gap-2 text-gray-800 bg-gray-50 p-2 rounded shadow-sm hover:bg-gray-100 transition"
                    >
                    <input
                        type="checkbox"
                        checked={choosedColumns.includes(column)}
                        className="h-4 w-4 text-blue-600 border-gray-400 rounded focus:ring-blue-500"
                        onChange={() => {
                        setChoosedColumns((prev) =>
                            prev.includes(column)
                            ? prev.filter((v) => v !== column)
                            : [...prev, column]
                        );
                        }}
                    />
                    <span className="truncate">{column}</span>
                    </label>
                ))}
            </div>


        )}
        </>
    )

    
    
}

function DisplayImages({images}){


        return (
        <div className="mt-6 space-y-6">
            {Object.entries(images).map(([categorie, dict]) => (
                <div key={categorie} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{categorie}</h3>
                <div className="flex flex-wrap gap-4">
                    {Object.entries(dict).map(([nom, image]) => (
                    <div key={nom} className="flex flex-col items-center">
                        <a href={image}
                        target="_blank"
                        rel="noopener noreferrer">
                            <img
                            src={image}
                            alt={nom}
                            className="w-32 h-32 object-cover rounded-md border border-gray-300"
                            />
                        </a>
                        <span className="text-sm text-gray-700 mt-1 truncate">{nom}</span>
                    </div>
                    ))}
                </div>
                </div>
            ))}
        </div>
    )
    }