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


import { useEffect,useState,useCallback } from 'react'
import Dropzone from 'react-dropzone'
import DatePicker from "react-datepicker"

export function UploadForm(){

    const [reload,setReload]=useState(0)
    const [succes,setSucces]=useState(false)
    const [erreur,setErreur]=useState("")
    const [selection,setSelection]=useState(0)

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
        <p className="mt-4 text-red-600 font-medium">
            {erreur}
        </p>
        )}
        {succes && (
  <>
    <DateUploadForm />
          
    
  </>
)}
    
      </>
    )
}


export function DateUploadForm(){
  const [date,setDate]=useState(null)
    

  const [rollingInterval,setRollingInterval]=useState(0)
  const [rollingIntervalType,setRollingIntervalType]=useState("")
  const [attrList,setAttrList]=useState([])
  const [erreur,setErreur]=useState("")
  const [succes,setSucces]=useState(false)


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
    if (rollingInterval===0 || attrList.length===0 || !date || rollingIntervalType===""){
      setErreur("Veuillez renseigner tous les champs")
      return ;
    }
    const response=await fetch("http://localhost:8000/api/preprocessing",{
      method:"POST",
      credentials:"include",
      body:JSON.stringify({
        year:date.getFullYear(),
        month:date.getMonth()+1,
        rollingIntervalType: rollingIntervalType,
        rollingInterval: rollingInterval,
        attrList: attrList
      })
    })
    if (!response.ok){
      setErreur(response.error)
      setSucces(false)
    }
    else{
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
      className="mt-4 w-48 px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-700"

  />
  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez sur quelles caractéristiques vous voulez détecter les outliers 
  </h4>

  {attributs.map((attr)=>(
    <label key={attr} className='text-gray-800'>
      <input type='checkbox'
      checked={attrList.includes(attr)}
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

  <h4 className="text-lg font-semibold mt-8 mb-4 text-gray-800">
    Indiquez sur quelle durée vous voulez que soit votre rollingInterval (en nombre de points ou en durée)
  </h4>
  <button
  onClick={()=>setRollingIntervalType("Duree")}
  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
  >
    Durée
  </button>
  <button
  onClick={()=>setRollingIntervalType("nb")}
  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
  >
    Nombre de données
  </button>

  {rollingIntervalType &&(
    <>
    {rollingIntervalType==="nb" ? <>
    <label for="nbPoints" className='text-gray-800'>Nombre de points</label>
    <input type='number' min="2" max="10" id="nbPoints" name="nbPoints"
    onChange={(e)=>setRollingInterval(e.target.value)}
    >
    
    </input>
    
    </> 
      : 
      
    <>
    <select value={rollingInterval} id="choixDuree"
    onChange={(e)=>{setRollingInterval(e.target.value)}}>Choisir une durée
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
        <p className="mt-4 text-red-600 font-medium">
            {erreur}
        </p>
        )}
    <button
    onClick={()=>preprocessData()}
    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition">
      Confirmer</button>

    {succes &&(
      <> 
      <SelectProcess />
      
      </>
    )}
          
</>


  )
}

export function SelectProcess(){


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
              <span className="text-gray-700">
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
                <span className="text-gray-700">
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