import { DisplayImages } from "./Stat";
import { useChoosedData } from "../menu/Menu"
import { useState,useEffect } from "react"


export function Trends(){
    const {mois,annee,catList} =useChoosedData()
    const [chosenHopInterval,setChosenHopInterval]=useState("")
    const [chosenHopValue,setChosenHopValue]=useState(null)
    const [chosenFreq,setChosenFreq]=useState("")
    const [images,setImages]=useState({})
    const [erreur,setErreur]=useState("")
    const [isLoading,setIsLoading]=useState(false)
    async function processData(){
        setErreur("")
        setIsLoading(true)
        if (chosenHopInterval==="" || !chosenHopValue ||chosenFreq===""){
        setErreur("Veuillez indiquer tous les paramètres")
        return ;
        }
        // class TrendsRequest(BaseModel):
        //     year:int|None
        //     month:int|None
        //     categories:List[str]|None
        //     hopInterval:Literal["seconds", "minutes", "hours", "days", "weeks"]
        //     hopValue: int
        //     freq:Literal["10s", "30s", "min", "5min", "15min","30min","h","D","W","M","Y"]
        const response=await fetch("http://localhost:8000/api/trends",{
        method:"POST",
        credentials:"include",
        headers: {
            "Content-Type": "application/json"
        },
        body:JSON.stringify({
            year:annee,
            month:mois,
            categories:catList,
            hopInterval:chosenHopInterval,
            hopValue:chosenHopValue,
            freq:chosenFreq
        })
        })
        setIsLoading(false)
        if (!response.ok){
            const errData = await response.json().catch(() => ({}))
            console.log("Erreur response:", errData)
            setErreur(errData.detail || `Erreur ${response.status}`)
            setImages([])
        }
        else{
            console.log("Traitement réussi")
            setErreur("")
            const data= await response.json()
            console.log(data)
            setImages(data.images)

            
        }
    }

    return(

        <>
        <ChooseParameters 
            setChosenHopInterval={setChosenHopInterval}
            setChosenHopValue={setChosenHopValue} 
            setChosenFreq={setChosenFreq}
        />
        {erreur && (
            <p className="text-red-600 font-semibold bg-red-50 border border-red-200 rounded-lg px-4 py-2 mt-4">
            {erreur}
            </p>
        )}
        {isLoading && (
            <p className="text-gray-700 font-medium bg-gray-100 border border-gray-200 rounded-lg px-4 py-2 mt-2">
                Chargement...
            </p>
        )}
        {(chosenHopInterval!=="" && chosenFreq!="" && chosenHopValue) && (
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

function ChooseParameters({setChosenHopInterval, setChosenHopValue, setChosenFreq}) {
    //généré par IA, il est plus de minuit et c'est juste un forms pour envoyer des paramètres au backend
    const hopIntervalOptions = ["seconds", "minutes", "hours", "days", "weeks"];
    const freqOptions = [
        { value: "10s", label: "10 secondes" },
        { value: "30s", label: "30 secondes" },
        { value: "min", label: "1 minute" },
        { value: "5min", label: "5 minutes" },
        { value: "15min", label: "15 minutes" },
        { value: "30min", label: "30 minutes" },
        { value: "h", label: "1 heure" },
        { value: "D", label: "1 jour" },
        { value: "W", label: "1 semaine" },
        { value: "M", label: "1 mois" },
        { value: "Y", label: "1 an" }
    ];

    const [localHopInterval, setLocalHopInterval] = useState("");
    const [localHopValue, setLocalHopValue] = useState("");
    const [localFreq, setLocalFreq] = useState("");

    useEffect(() => {
        setChosenHopInterval(localHopInterval);
    }, [localHopInterval, setChosenHopInterval]);

    useEffect(() => {
        setChosenHopValue(localHopValue ? parseInt(localHopValue) : null);
    }, [localHopValue, setChosenHopValue]);

    useEffect(() => {
        setChosenFreq(localFreq);
    }, [localFreq, setChosenFreq]);

    return (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Paramètres de l'analyse
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Hop Interval */}
                <div className="flex flex-col">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Intervalle de saut
                    </label>
                    <select
                        value={localHopInterval}
                        onChange={(e) => setLocalHopInterval(e.target.value)}
                        className="flex-1 px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    >
                        <option value="" className="text-gray-500">Sélectionner...</option>
                        {hopIntervalOptions.map((option) => (
                            <option key={option} value={option} className="text-gray-900">
                                {option}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Hop Value */}
                <div className="flex flex-col">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Valeur de saut
                    </label>
                    <input
                        type="number"
                        min="1"
                        value={localHopValue}
                        onChange={(e) => setLocalHopValue(e.target.value)}
                        placeholder="Ex: 30"
                        className="flex-1 px-3 py-2 bg-white text-gray-900 placeholder-gray-400 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    />
                </div>

                {/* Frequency */}
                <div className="flex flex-col">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Fréquence d'échantillonnage
                    </label>
                    <select
                        value={localFreq}
                        onChange={(e) => setLocalFreq(e.target.value)}
                        className="flex-1 px-3 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    >
                        <option value="" className="text-gray-500">Sélectionner...</option>
                        {freqOptions.map((option) => (
                            <option key={option.value} value={option.value} className="text-gray-900">
                                {option.label}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Info tooltip */}
            <div className="mt-4 text-sm text-gray-700 bg-blue-50 border border-blue-200 rounded-lg p-3">
                <span className="font-semibold">💡 Info :</span> L'intervalle de saut détermine 
                la taille de la fenêtre glissante pour l'analyse des tendances.
            </div>
        </div>
    );
}