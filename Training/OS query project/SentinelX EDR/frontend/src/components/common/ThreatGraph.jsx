import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const cn = (...inputs) => twMerge(clsx(inputs));

const ThreatGraph = ({ nodes, links }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !nodes || !links) return;

    // Clear previous SVG
    d3.select(containerRef.current).selectAll('*').remove();

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    const svg = d3.select(containerRef.current)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .call(d3.zoom().on('zoom', (event) => {
        g.attr('transform', event.transform);
      }));

    const g = svg.append('g');

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(30));

    // Draw links
    const link = g.append('g')
      .attr('stroke', '#374151') // border color
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', 2);

    // Node colors
    const getNodeColor = (type, isSuspicious) => {
      if (isSuspicious) return '#EF4444'; // danger
      switch (type) {
        case 'process': return '#3B82F6'; // primary
        case 'file': return '#10B981'; // accent
        case 'network': return '#F59E0B'; // warning
        case 'user': return '#8B5CF6'; // secondary
        default: return '#9CA3AF'; // textMuted
      }
    };

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => d.isSuspicious ? 12 : 8)
      .attr('fill', d => getNodeColor(d.type, d.isSuspicious))
      .attr('stroke', '#111827')
      .attr('stroke-width', 2)
      .call(drag(simulation));

    // Node labels
    const label = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .attr('dx', 15)
      .attr('dy', 4)
      .text(d => d.label)
      .attr('fill', '#F9FAFB') // textMain
      .attr('font-size', '12px')
      .attr('font-family', 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"');

    // Link labels (relationship)
    const edgeLabel = g.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .text(d => d.relationship)
      .attr('fill', '#9CA3AF') // textMuted
      .attr('font-size', '10px')
      .attr('text-anchor', 'middle');

    // Tick function
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);

      edgeLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2 - 5);
    });

    // Drag behavior
    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      
      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      
      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      
      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }

    return () => {
      simulation.stop();
    };
  }, [nodes, links]);

  return (
    <div ref={containerRef} className="w-full h-full bg-background rounded-xl overflow-hidden cursor-move"></div>
  );
};

export default ThreatGraph;
