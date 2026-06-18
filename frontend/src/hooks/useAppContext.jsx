import { createContext, useContext, useState } from 'react'
import { JOB_DESCRIPTION } from '../data/candidates'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [candidates, setCandidates] = useState([])
  const [jobDescription, setJobDescription] = useState(JOB_DESCRIPTION)
  const [activeJob] = useState('Frontend Engineer')

  const addCandidate = (candidate) => {
    setCandidates(prev => [...prev, candidate])
  }

  return (
    <AppContext.Provider value={{
      candidates,
      setCandidates,
      jobDescription,
      setJobDescription,
      activeJob,
      addCandidate,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => useContext(AppContext)
