'use client'

import Image from "next/image";
import styles from "./page.module.scss";
import ConfettiScreen from "./Confetti";
import { useEffect, useState } from "react";

export default function Home() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetch('http://localhost:8000/api/hello')
      .then(res => res.json())
      .then(data => setMessage(data.message))
  }, [])
  
  return (
    <div className={styles.page}>
    <div className={styles.pageLayout}>
      <header className={styles.pageHeader}>
      <Image src="/tines.svg" alt="tines" priority width={100} height={30} />

      </header>
      <div className={styles.body}>
        <h1 className={styles.pageTitle}>{message}!</h1>

        <p>
          Great to see you here. This environment is set up to ensure everything is working correctly before your technical interview.
        </p>

        <p>
          We'll send you a link to the technical challenge repository at the time of your interview, which uses the same packages as this sandbox.
        </p>

        <p>
          If you can see this page and the illustration below, your development environment is properly configured and you're all set!
        </p>
      </div>
      <div className={styles.form}>

      </div>
      <div className={styles.illustration}>
        <Image src="/illustration.svg" alt="illustration" priority width={500} height={50} />
        <ConfettiScreen shouldStart amount={300} />
      </div>
      <footer className={styles.footer}>© Tines</footer>
    </div>
  </div>
  );
}
