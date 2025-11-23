import React, { useMemo } from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from 'recharts';

const CustomTooltip = React.memo(({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white/95 dark:bg-[#1A1A1A]/95 backdrop-blur-md border border-gray-200 dark:border-[#333] p-3 rounded-lg shadow-xl">
        <p className="font-bold text-gray-900 dark:text-white mb-1 text-xs">{data.name}</p>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-gray-500 dark:text-gray-400">Уровень:</span>
          <span className="font-mono font-bold" style={{ color: data.fill }}>{data.current}%</span>
        </div>
      </div>
    )
  }
  return null
});

const SkillRadar = React.memo(({ skills, currentLevels, targetLevels }) => {
  const colors = [
    '#FF3B77', '#E02A64', '#C12ABC', '#9F3BF2', '#7E3BF2', '#5C3BF2', '#3B5BF2'
  ];

  const data = useMemo(() => 
    (skills || [])
      .map((skill, index) => ({
        name: skill.name,
        current: currentLevels[skill.id] || 0,
        target: targetLevels[skill.id] || 0,
        fill: colors[index % colors.length]
      }))
      .sort((a, b) => b.current - a.current),
    [skills, currentLevels, targetLevels, colors]
  );

  return (
    <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl p-5 flex flex-col h-full">
      <div className="mb-3">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">Орбита навыков</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">Прогресс vs Цели</p>
      </div>
      
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart 
            cx="50%" 
            cy="50%" 
            innerRadius="20%" 
            outerRadius="100%" 
            barSize={12} 
            data={data}
            startAngle={180} 
            endAngle={-180}
          >
            <RadialBar
              minAngle={15}
              background={{ fill: '#f3f4f6', className: 'dark:fill-[#222]' }}
              clockWise
              dataKey="current"
              cornerRadius={8}
            />
            <Tooltip content={<CustomTooltip />} cursor={false} />
          </RadialBarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-2 mt-4 border-t border-gray-100 dark:border-[#222] pt-3">
        {data.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 overflow-hidden">
            <span 
              className="w-2 h-2 rounded-full flex-shrink-0" 
              style={{ backgroundColor: entry.fill }}
            />
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 truncate">
                {entry.name}
              </span>
              <div className="flex gap-1 text-[10px]">
                <span className="text-gray-900 dark:text-gray-100 font-mono">{entry.current}%</span>
                <span className="text-gray-400">/ {entry.target}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
});

export default SkillRadar;