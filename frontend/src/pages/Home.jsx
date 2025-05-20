import React, { useEffect, useState } from "react";

function Home() {
  const [players, setPlayers] = React.useState([]);

  React.useEffect(() => {
    fetch("http://localhost:8000/players/")
      .then((res) => res.json())
      .then((data) => setPlayers(data.players))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div>
      <h1>Players</h1>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Full Name</th>
            <th>Jersey</th>
            <th>Team ID</th>
            <th>Injury Status</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player) => (
            <tr key={player.id}>
              <td>{player.fullName}</td>
              <td>{player.jersey}</td>
              <td>{player.proTeamId}</td>
              <td>{player.injuryStatus}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Home;
