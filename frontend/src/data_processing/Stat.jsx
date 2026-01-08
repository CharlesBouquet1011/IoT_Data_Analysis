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
import { useState } from "react"
import { useChoosedData } from "../menu/Menu"


export function Statistiques(){
    const {mois,annee} =useChoosedData()
    const [choosedColumns,setChoosedColumns]=useState([]) //on passera sur l'erreur de conjugaison, le code fonctionne
    const [images,setImages]=useState({})
    const [erreur,setErreur]=useState("")
    async function processData(){
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
    
        {choosedColumns.length!==0 &&(
            <>
            1ère colonne choisie: {choosedColumns[0]}
            <button onClick={()=>processData()}> Afficher les résultats </button>
            </>
        )}
        </>
    )
}



function ChooseColumns({choosedColumns,setChoosedColumns}){
    const columns=["Bandwidth","Coding_rate","GW_EUI","SF","freq","modu","adr"]
    const {mois,annee}=useChoosedData()
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

    function DisplayImages({paths}){


        return (
        <>
        
        </>)
    }
    
}