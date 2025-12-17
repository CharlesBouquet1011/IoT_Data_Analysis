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

    const [reload,setReload]=useState(0)
    const [succes,setSucces]=useState(false)
    const [erreur,setErreur]=useState("")

    async function sendFile(file){
    try{
      console.log("envoi fichier")
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
      setReload(1^reload)
      setErreur("")
    }
    else{
      const data=await response.json()

      console.log(data.error)
      setSucces(false)
      setErreur(data.error)
    }
    }
    catch (err){
      console.log("Erreur lors de l'envoi du fichier: ",err)
      setSucces(false)
    }
    

  }
  

    return(<>
    <div className="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow-md space-y-8">

        <Dropzone
        onDrop={acceptedFiles => sendFile(acceptedFiles[0])}
        multiple={false}
        accept={{ 'text/json': ['.json'] }}
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

        {erreur && (
        <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2">
            {erreur}
        </p>
        )}
        {succes && (
  <>
    <DateUploadForm />
          
    
  </>
)}
    </div>
      </>
    )
}


export function DateUploadForm(){
  const [date,setDate]=useState(null)
    

  const [rollingInterval,setRollingInterval]=useState(0)
  const [rollingIntervalType,setRollingIntervalType]=useState("")
  const [attrList,setAttrList]=useState([])
  const [erreur,setErreur]=useState("")

  const durations = [
  { label: "1 jour", value: "1d" },
  { label: "7 jours", value: "7d" },
  { label: "1 mois", value: "1m" },
  { label: "3 mois", value: "3m" },
  { label: "6 mois", value: "6m" },
  { label: "1 an", value: "1y" },
];
const attributs=["Airtime","BitRate","rssi","lsnr"] //rajouter des attributs ici si on veut

  async function preprocessData() {
    console.log("confirmation")
    console.log("roll :",rollingInterval)
    if (!rollingInterval || attrList.length===0 || !date || rollingIntervalType===""){
      setErreur("Veuillez renseigner tous les champs")
      return ;
    }
    const response=await fetch("http://localhost:8000/api/preprocessing",{
      method:"POST",
      credentials:"include",
      headers: {
        "Content-Type": "application/json"
      },
      body:JSON.stringify({
        year:date.getFullYear(),
        month:date.getMonth()+1,
        rollingIntervalType: rollingIntervalType,
        rollingInterval: rollingIntervalType === "nb" ? parseInt(rollingInterval, 10) : rollingInterval,
        attrList: attrList,
      })
    })
    console.log("Response status:", response.status)
    console.log("Response ok:", response.ok)
    if (!response.ok){
      const errData = await response.json().catch(() => ({}))
      console.log("Erreur response:", errData)
      setErreur(errData.error || `Erreur ${response.status}`)
      setSucces(false)
    }
    else{
      console.log("Prétraitement réussi")
      setErreur("")
      setSucces(true)
    }
  }

  return(

<>
  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
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
  />
  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez sur quelles caractéristiques vous voulez détecter les outliers 
  </h4>
  <div className="grid grid-cols-2 gap-4 mt-2">

  {attributs.map((attr)=>(
    <label key={attr} className='text-gray-800'>
      <input type='checkbox'
      checked={attrList.includes(attr)}
      className="h-4 w-4 text-blue-600 border-gray-400 rounded focus:ring-blue-500"
      onChange={()=>{
        setAttrList(prev => {
          if (prev.includes(attr)) {
            return prev.filter(v => v !== attr);
          }
          return [...prev, attr];
        });
      
            }}
      />
      {attr}
    </label>
  ))}
  </div>
  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez sur quelle durée vous voulez que soit votre rollingInterval (en nombre de points ou en durée)
  </h4>
  <div className="flex gap-4">
    <button
    onClick={()=>{setRollingIntervalType("Duree")
      setRollingInterval("1d")

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
    onClick={()=>{setRollingIntervalType("nb")

      setRollingInterval(0)
    }
  }

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
  )}

    {erreur && (
        <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2">
            {erreur}
        </p>
        )}
    <button
    onClick={()=>preprocessData()}
    className="w-full bg-blue-600 hover:bg-blue-700 text-white
             font-semibold py-3 rounded-lg transition">
      Confirmer</button>
          
</>

  )
}

// Fonction pour choisir le processus à appliquer après l'upload
export function SelectProcess(){
  const [selection, setSelection] = useState(0)

  return(

    <>
    <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
      Choisissez ce que vous voulez faire du fichier
    </h4>
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
                TEXTE DESC SELECTION
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
                  TEXTE AIDE SELECTION
                </span>
              </span>
              <small className="text-xs text-red-500">
                WARNING
              </small>
            </label>
          </td>
        </tr>
      </tbody>
    </table>
    
    {/* exemples d'utilisation, il faudra choisir les nombres que vous voulez pour mettre les fonctions que vous voulez
    et rajouter des cases dans le tableau pour laisser le choix à l'utilisateur
    */}
    {/*succes && selection===1 ? <PreTraitement reload={reload} />: <></> */}
    {/*succes && selection===2 ? <Verification reload={reload} /> : <></>*/}
    </>
  )
}