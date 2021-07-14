var labelType, useGradients, nativeTextSupport, animate;

function init(){
    //init data
    var json = "{id:\"nodeROOT\", name:\"UFONET\", data:{}, children:[{id:\"nodeGLOBAL\", name:\"GLOBAL\", data:{}, children:[{id:\"nodeBOARD\", name:\"BOARD\", data:{}, children:[{id:\"nodeSUPPORT\", name:\"SUPPORT\", data:{}, children:[]}]}, {id:\"nodeGRID\", name:\"GRID\", data:{}, children:[{id:\"nodeSTATS2\", name:\"STATS\", data:{}, children:[]}]}, {id:\"nodeWARGAMES\", name:\"WARGAMES\", data:{}, children:[{id:\"nodeBOTNET2\", name:\"BOTNET\", data:{}, children:[]},  {id:\"nodeSUPPORT2\", name:\"SUPPORT\", data:{}, children:[]}]}, {id:\"nodeLINKS\", name:\"LINKS\", data:{}, children:[]}, {id:\"nodeSTREAMS\", name:\"STREAMS\", data:{}, children:[]}, {id:\"nodeNETWORK\", name:\"NETWORK\", data:{}, children:[{id:\"nodeRADAR\", name:\"RADAR\", data:{}, children:[]}, {id:\"nodeWARPS2\", name:\"WARPS\", data:{}}]}]}, {id:\"nodeSHIP\", name:\"SHIP\", data:{}, children:[{id:\"nodeEXPLORE\", name:\"EXPLORE\", data:{}, children:[{id:\"nodeINSPECTION\", name:\"INSPECTION\", data:{}, children:[]}, {id:\"nodeABDUCTION\", name:\"ABDUCTION\", data:{}, children:[]}, {id:\"nodeDORKING\", name:\"DORKING\", data:{}, children:[{id:\"nodeZOMBIES2\", name:\"ZOMBIES\", data:{}, children:[]}]} ]}, {id:\"nodeBOTNET\", name:\"BOTNET\", data:{}, children:[{id:\"nodeZOMBIES\", name:\"ZOMBIES\", data:{}, children:[]}, {id:\"nodeALIENS\", name:\"ALIENS\", data:{}, children:[]}, {id:\"nodeDROIDS\", name:\"DROIDS\", data:{}, children:[]}, {id:\"nodeUCAVs\", name:\"UCAVs\", data:{}, children:[]},  {id:\"nodeXML-RPCs\", name:\"XML-RPCs\", data:{}, children:[]}, {id:\"NTPs\", name:\"NTPs\", data:{}, children:[]}, {id:\"DNSs\", name:\"DNSs\", data:{}, children:[]}, {id:\"SNMPs\", name:\"SNMPs\", data:{}, children:[]} ]}, {id:\"nodeATTACKS\", name:\"ATTACKS\", data:{}, children:[{id:\"nodeBOTNET4\", name:\"BOTNET\", data:{}, children:[]}, {id:\"nodeEXTRA\", name:\"EXTRA\", data:{}, children:[{id:\"nodeLAYER7\", name:\"LAYER-7\", data:{}, children:[]}, {id:\"nodeLOIC\", name:\"LOIC\", data:{}, children:[]}, {id:\"nodeLORIS\", name:\"LORIS\", data:{}, children:[]},{id:\"nodeUFOSYN\", name:\"UFOSYN\", data:{}, children:[]},{id:\"nodeFRAGGLE\", name:\"FRAGGLE\", data:{}, children:[]},{id:\"nodeUFORST\", name:\"UFORST\", data:{}, children:[]},{id:\"nodeSPRAY\", name:\"SPRAY\", data:{}, children:[]},{id:\"nodeSMURF\", name:\"SMURF\", data:{}, children:[]},{id:\"nodeXMAS\", name:\"XMAS\", data:{}, children:[]},{id:\"nodeDROPER\", name:\"DROPER\", data:{}, children:[]},{id:\"nodeSNIPER\", name:\"SNIPER\", data:{}, children:[]},{id:\"nodeTACHYON\", name:\"TACHYON\", data:{}, children:[]},{id:\"nodePINGER\", name:\"PINGER\", data:{}, children:[]},{id:\"nodeMONLIST\", name:\"MONLIST\", data:{}, children:[]},{id:\"nodeUFOACK\", name:\"UFOACK\", data:{}, children:[]},{id:\"nodeOVERLAP\", name:\"OVERLAP\", data:{}, children:[]},{id:\"nodeUFOUDP\", name:\"UFOUDP\", data:{}, children:[]},{id:\"nodeNUKE\", name:\"NUKE\", data:{}, children:[]}]}]}, {id:\"nodeTV\", name:\"TV\", data:{}, children:[]}, {id:\"nodeBROWSER\", name:\"BROWSER\", data:{}, children:[]}, {id:\"nodeGAMES\", name:\"GAMES\", data:{},  children:[]}, {id:\"nodeNEWS\", name:\"NEWS\", data:{}, children:[]}, {id:\"nodeMISSIONS\", name:\"MISSIONS\", data:{}, children:[]}, {id:\"nodeSTATS\", name:\"STATS\", data:{}, children:[]}, {id:\"nodeWARPS\", name:\"WARPS\", data:{}}]}]}";
    //end

    var getTree = (function() {
        var i = 0;
        return function(nodeId, level) {
          var subtree = eval('(' + json.replace(/id:\"([a-zA-Z0-9]+)\"/g, 
          function(all, match) {
            return "id:\"" + match + "_" + i + "\""  
          }) + ')');
          $jit.json.prune(subtree, level); i++;
          return {
              'id': nodeId,
              'children': subtree.children
          };
        };
    })();
    
    $jit.ST.Plot.NodeTypes.implement({
        'nodeline': {
          'render': function(node, canvas, animating) {
                if(animating === 'expand' || animating === 'contract') {
                  var pos = node.pos.getc(true), nconfig = this.node, data = node.data;
                  var width  = nconfig.width, height = nconfig.height;
                  var algnPos = this.getAlignedPos(pos, width, height);
                  var ctx = canvas.getCtx(), ort = this.config.orientation;
                  ctx.beginPath();
                  if(ort == 'left' || ort == 'right') {
                      ctx.moveTo(algnPos.x, algnPos.y + height / 2);
                      ctx.lineTo(algnPos.x + width, algnPos.y + height / 2);
                  } else {
                      ctx.moveTo(algnPos.x + width / 2, algnPos.y);
                      ctx.lineTo(algnPos.x + width / 2, algnPos.y + height);
                  }
                  ctx.stroke();
              } 
          }
        }
          
    });

    //init Spacetree
    var st = new $jit.ST({
        'injectInto': 'infovis',
        duration: 800,
        transition: $jit.Trans.Quart.easeInOut,
        levelDistance: 160,
        levelsToShow: 1,
        Node: {
            height: 30,
            width: 60,
            type: 'nodeline',
            color:'yellow',
            overridable: true,
            lineWidth: 1
        },
 
        Edge: {
 	    height: 30,
            width: 60,
            color:'red',
            overridable: true,
            lineWidth: 1
        },
        
        request: function(nodeId, level, onComplete) {
          var ans = getTree(nodeId, level);
          onComplete.onComplete(nodeId, ans);  
        },

        onCreateLabel: function(label, node){
            label.id = node.id;            
            label.innerHTML = node.name;
            label.onclick = function(){
                st.onClick(node.id);
            };
            var style = label.style;
            style.width = 180 + 'px';
            style.height = 80 + 'px';            
            style.cursor = 'pointer';
            style.color = 'yellow';
            style.fontSize = '14px';
            style.textDecoration = 'underline';
            style.paddingTop = '4px';
        },

        onBeforePlotNode: function(node){
            if (node.selected) {
                node.data.$color = "#ff7";
            }
            else {
                delete node.data.$color;
            }
        },
        
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = "green";
                adj.data.$lineWidth = 1;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    st.loadJSON(eval( '(' + json + ')' ));
    st.compute();
    st.onClick(st.root);
    //end

   function get(id) {
      return document.getElementById(id);  
    };
    var top = get('r-top'), 
    left = get('r-left'), 
    bottom = get('r-bottom'), 
    right = get('r-right');  
    function changeHandler() {
        if(this.checked) {
            top.disabled = bottom.disabled = right.disabled = left.disabled = true;
            st.switchPosition(this.value, "animate", {
                onComplete: function(){
                    top.disabled = bottom.disabled = right.disabled = left.disabled = false;
                }
            });
        }
    };  
    top.onchange = left.onchange = bottom.onchange = right.onchange = changeHandler;
}
