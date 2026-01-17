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


import { useState } from 'react'
import Dropzone from 'react-dropzone'
import DatePicker from "react-datepicker"

export function UploadForm(){
    const [isLoading,setIsLoading]=useState(false)
    const [reload,setReload]=useState(0)
    const [succes,setSucces]=useState(false)
    const [processed,setProcessed]=useState(false)
    const [erreur,setErreur]=useState("")

    async function sendFile(file){
    try{
      console.log("envoi fichier")
      setIsLoading(true)
      setErreur("")
      setSucces(false) //pour pas qu'on puisse utiliser les composants suivants lorsqu'un fichier est en train d'être réupload (évitera probablement des bugs)
      const formdata=new FormData()
      formdata.append("file",file)
      const response = await fetch("http://localhost:8000/api/upload/", { //comme avant
            method: "POST",
            credentials:'include',
            body:formdata

          });
    if (response.ok){
      console.log("Fichier envoyé avec succès")
      setSucces(true)
      setReload(r => r ^ 1)
      setErreur("")
      setIsLoading(false)
    }
    else{
      const data=await response.json()
      setIsLoading(false)
      console.log(data.error)
      setSucces(false)
      setErreur(data.error)
    }
    }
    catch (err){
      console.log("Erreur lors de l'envoi du fichier: ",err)
      setSucces(false)
      setIsLoading(false)
    }
    

  }
  

    return(<>
    

        <Dropzone
        onDrop={acceptedFiles => sendFile(acceptedFiles[0])}
        multiple={false}
        accept={{ 'application/json': ['.json'] }}
      >
        {({ getRootProps, getInputProps }) => (
          <section>
            <div
              {...getRootProps()}
              className="cursor-pointer border-2 border-dashed border-gray-300 rounded-md p-8 flex flex-col items-center justify-center hover:border-indigo-500 transition-colors"
            >
              <input {...getInputProps()} />
              <p className="text-gray-500 text-center text-sm">
                Glissez-déposez le fichier ici ou cliquez pour choisir un fichier
              </p>
            </div>
          </section>
        )}
      </Dropzone>
        {isLoading && (
            <p className="text-gray-700 font-medium bg-gray-100 border border-gray-200 rounded-lg px-4 py-2 mt-2">
                Chargement...
            </p>
        )}
        {erreur && (
        <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2">
            {erreur}
        </p>
        )}
        {succes && (
  <>
    <DateUploadForm setProcessed={setProcessed} processed={processed} />
  </>
)}

        
      </>
    )
}


export function DateUploadForm({ setProcessed, processed }){
  const [isLoading,setIsLoading]=useState(false)
  const [rollingInterval,setRollingInterval]=useState(0)
  const [rollingIntervalType,setRollingIntervalType]=useState("")
  const [attrList,setAttrList]=useState([])
  const [erreur,setErreur]=useState("")

  const durations = [
  { label: "30 minutes", value: "30min" },
  { label: "1 heure", value: "1h" },
  { label: "2 heures", value: "2h" },
  { label: "6 heures", value: "6h" },
  { label: "12 heures", value: "12h" },
  { label: "1 jour", value: "1D" },
  { label: "7 jours", value: "7D" },
  { label: "1 mois", value: "30D" },
  { label: "3 mois", value: "90D" },
  { label: "6 mois", value: "180D" },
  { label: "1 an", value: "365D" },
];
const attributs=["Airtime","BitRate","rssi","lsnr"] //rajouter des attributs ici si on veut

  async function preprocessData() {
    console.log("confirmation")
    console.log("roll :",rollingInterval)
    if (!rollingInterval || attrList.length===0 || rollingIntervalType===""){
      setErreur("Veuillez renseigner tous les champs")
      return ;
    }
    setIsLoading(true)
    const response=await fetch("http://localhost:8000/api/preprocessing",{
      method:"POST",
      credentials:"include",
      headers: {
        "Content-Type": "application/json"
      },
      body:JSON.stringify({
        rollingIntervalType: rollingIntervalType,
        rollingInterval: rollingIntervalType === "nb" ? parseInt(rollingInterval, 10) : rollingInterval,
        attrList: attrList,
      })
    })
    console.log("Response status:", response.status)
    console.log("Response ok:", response.ok)
    if (!response.ok){
      setIsLoading(false)
      const errData = await response.json().catch(() => ({}))
      console.log("Erreur response:", errData)
      setErreur(errData.error || `Erreur ${response.status}`)
    }
    else{
      setIsLoading(false)
      console.log("Prétraitement réussi")
      setErreur("")
      if (typeof setProcessed === 'function') setProcessed(true)
    }
  }

  return(

<>
  {/* <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez à quel mois correspond votre donnée
  </h4>
  <DatePicker selected={date}
    onChange={(date)=>setDate(date)}
    showMonthYearPicker
    dateFormat="MM/yyyy"
    placeholderText='Choisir un mois'
className="w-full px-4 py-2 border border-gray-300 rounded-lg
             bg-white text-gray-800
             focus:outline-none focus:ring-2 focus:ring-blue-500"
  /> */}
  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez sur quelles caractéristiques vous voulez détecter les outliers 
  </h4>
  <div className="grid grid-cols-2 gap-4 mt-2">

  {attributs.map((attr)=>(
    <label key={attr} className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer text-gray-800">
      <input
        type="checkbox"
        checked={attrList.includes(attr)}
        className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
        onChange={() => {
          setAttrList(prev => {
            if (prev.includes(attr)) {
              return prev.filter(v => v !== attr);
            }
            return [...prev, attr];
          });
        }}
      />
      <span className="text-sm text-gray-800">{attr}</span>
    </label>
  ))}
  </div>
  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez sur quelle durée vous voulez que soit votre rollingInterval (en nombre de points ou en durée)
  </h4>
  <div className="flex gap-4">
    <button
    onClick={()=>{setRollingIntervalType("Duree")
      setRollingInterval("30min")

    }}
    className={`flex-1 py-2 rounded-lg font-semibold transition
    ${rollingIntervalType === "Duree"
      ? "bg-blue-600 text-white"
      : "bg-gray-200 text-gray-800 hover:bg-gray-300"}
  `}
    >
      Durée
    </button>
    <button
    onClick={() => { setRollingIntervalType("nb"); setRollingInterval(0); }}

    className={`flex-1 py-2 rounded-lg font-semibold transition
        ${rollingIntervalType === "nb"
          ? "bg-blue-600 text-white"
          : "bg-gray-200 text-gray-800 hover:bg-gray-300"}
      `}
    >
      Nombre de données
    </button>
  </div>
  {rollingIntervalType &&(
    <div className="mt-4">
    <>
    {rollingIntervalType==="nb" ? <>
    <input type='number' min="2" max="10" id="nbPoints" name="nbPoints"
    onChange={(e)=>setRollingInterval(e.target.value)}
    className="w-full px-4 py-2 border border-gray-300 rounded-lg
             bg-white text-gray-800
             focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
    
    </input>
    
    </> 
      :
      
    <>
    <select value={rollingInterval} id="choixDuree"
    onChange={(e)=>{setRollingInterval(e.target.value)}}
    className="w-full px-4 py-2 border border-gray-300 rounded-lg
             bg-white text-gray-800
             focus:outline-none focus:ring-2 focus:ring-blue-500"
    >Choisir une durée
    {durations.map( d=>{
      //on peut faire du code supplémentaire ici en fait
      return(
      <option key={d.value} value={d.value}
      className='text-gray-800'
      >{d.label}</option>
      )
    })}
    </select>
    </>}
    
    </>
    </div>
  )}
    {isLoading && (
            <p className="text-gray-700 font-medium bg-gray-100 border border-gray-200 rounded-lg px-4 py-2 mt-2">
                Chargement...
            </p>
        )}

    {erreur && (
        <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2">
            {erreur}
        </p>
        )}
    {processed &&(
      <p className="text-green-700 font-semibold bg-green-50 border border-green-200 rounded-lg px-4 py-2">
          Les données ont bien été traitées choisissez maintenant le traitement des données à l'aide du menu
      </p> 
    )}
        <button
        onClick={()=>preprocessData()}
        className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white
            font-semibold py-3 rounded-lg transition">
          Confirmer</button>
          
</>

  )
}

// Fonction pour choisir le processus à appliquer après l'upload
// export function SelectProcess(){
//   const [selection, setSelection] = useState(0)

//   return(

//     <>
//     <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
//       Choisissez ce que vous voulez faire du fichier
//     </h4>
//     <table className="w-full max-w-xl border-collapse border border-gray-200">
//       <tbody>
//         <tr className="hover:bg-gray-50">
//           <td className="p-4 border border-gray-200">
//             <label className="flex items-center space-x-3 cursor-pointer">
//               <input
//                 type="radio"
//                 name="choix"
//                 value="1"
//                 onClick={() => setSelection(1)}
//                 className="form-radio text-indigo-600"
//               />
//               <span className="text-gray-800 font-medium">
//                 TEXTE DESC SELECTION
//               </span>
//             </label>
//           </td>
//           <td className="p-4 border border-gray-200">
//             <label className="flex flex-col space-y-2 cursor-pointer">
//               <span className="flex items-center space-x-3">
//                 <input
//                   type="radio"
//                   name="choix"
//                   value="2"
//                   onClick={() => setSelection(2)}
//                   className="form-radio text-indigo-600"
//                 />
//                 <span className="text-gray-800 font-medium">
//                   TEXTE AIDE SELECTION
//                 </span>
//               </span>
//               <small className="text-xs text-red-500">
//                 WARNING
//               </small>
//             </label>
//           </td>
//         </tr>
//       </tbody>
//     </table>
    
//     {/* exemples d'utilisation, il faudra choisir les nombres que vous voulez pour mettre les fonctions que vous voulez
//     et rajouter des cases dans le tableau pour laisser le choix à l'utilisateur
//     */}
//     {/*succes && selection===1 ? <PreTraitement reload={reload} />: <></> */}
//     {/*succes && selection===2 ? <Verification reload={reload} /> : <></>*/}
//     </>
//   )
// }