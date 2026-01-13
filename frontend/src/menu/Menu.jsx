import { useState,createContext,useContext,useEffect } from 'react'
import { UploadForm } from '../preprocessing/DropFile'
import DatePicker from "react-datepicker"
import {AnalysisMenu} from "../preprocessing/AnalysisMenu"
import { Statistiques } from '../data_processing/Stat'
import { Clustering } from '../data_processing/Clustering'
import { Regression } from '../data_processing/Regression'
import { Trends } from '../data_processing/Trends'
const DataContext = createContext();

export function MenuPrincipal(){
    const [selection,setSelection]=useState(0)

    return(
        <>
        <div className="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow-md space-y-8">
            <table className="w-full max-w-xl border-collapse border border-gray-200">
                <tbody>
                    <tr className="hover:bg-gray-50">
                    <td className="p-4 border border-gray-200">
                        <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                            type="radio"
                            name="choix"
                            value="1"
                            onClick={() => setSelection(1)}
                            className="form-radio text-indigo-600"
                        />
                        <span className="text-gray-800 font-medium">
                            Upload un nouveau fichier
                        </span>
                        </label>
                    </td>
                    <td className="p-4 border border-gray-200">
                        <label className="flex flex-col space-y-2 cursor-pointer">
                        <span className="flex items-center space-x-3">
                            <input
                            type="radio"
                            name="choix"
                            value="2"
                            onClick={() => setSelection(2)}
                            className="form-radio text-indigo-600"
                            />
                            <span className="text-gray-800 font-medium">
                            Faire un traitement sur des données précédemment upload
                            </span>
                        </span>
                        
                        </label>
                    </td>
                    </tr>
                </tbody>
            </table>
            
            {selection==1 && (
                <UploadForm />
            )}

            {selection ==2 && (<ChooseData />)}

            </div>
        </>



    )
}

export function ChooseData(){
    const categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Stat","Unconfirmed Data Up","Unconfirmed Data Down"]
    const [catList,setCatList]=useState([])
    const [month,setMonth]=useState(null)
    const [year,setYear]=useState(null)
    // var [mois,annee]=[null,null]
    const [traitement,setTraitement]=useState(0)

    // À vérifier et enlever si besoin
    const mois = month ? month.getMonth() + 1 : null
    const annee = year ? year.getFullYear() : null

    return(<>
    <h4>
        Remplissez uniquement les champs dont vous avez besoin pour restreindre la recherche
    </h4>
    <DatePicker selected={year}
        onChange={(date)=>setYear(date)}
        showYearPicker
        dateFormat="yyyy"
        placeholderText='Choisir une année'
    className="w-full px-4 py-2 border border-gray-300 rounded-lg
                 bg-white text-gray-800
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    <DatePicker selected={month}
        onChange={(date)=>setMonth(date)}
        showMonthYearPicker
        showFullMonthYearPicker={false}
        dateFormat="MM"
        placeholderText='Choisir un mois'
    className="w-full px-4 py-2 border border-gray-300 rounded-lg
                 bg-white text-gray-800
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />  
    

    <div className="grid grid-cols-2 gap-4 mt-2">
    
    {categories.map((cat)=>(
        <label key={cat} className='text-gray-800'>
        <input type='checkbox'
        checked={catList.includes(cat)}
        className="h-4 w-4 text-blue-600 border-gray-400 rounded focus:ring-blue-500"
        onChange={()=>{
            setCatList(prev => {
            if (prev.includes(cat)) {
                return prev.filter(v => v !== cat);
            }
            return [...prev, cat];
            });
        
                }}
        />
        {cat}
        </label>
    ))}
  </div>

    {(catList.length>0 || month || year) &&(
        <DataContext.Provider value={{catList,mois,annee}}>
            <AnalysisMenu onChoice={(choice)=>{ setTraitement(choice)}} />

            {traitement===1 &&(
                <Regression />
            )}
            {traitement===2 &&(
                <Trends />
            )}
            {traitement===3 && (
                <Clustering />
            )}
            {
                traitement===4 && (
                    <Statistiques/>
                )
            }
        </DataContext.Provider>

    )}

    </>)
}

export function useChoosedData(){
    const context=useContext(DataContext)
    if (!context){
        throw new Error('useCSRF doit être utilisé à l\'intérieur du DataContext Provider');
    }
    return context

}